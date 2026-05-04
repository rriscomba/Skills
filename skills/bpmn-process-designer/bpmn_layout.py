#!/usr/bin/env python3
"""
bpmn_layout.py  — Auto-layout engine for BPMN 2.0 XML
=====================================================
Input : JSON process specification  (spec.json)
Output: Valid BPMN 2.0 XML with full BPMNDiagram layout

Usage
-----
  python bpmn_layout.py spec.json [output.bpmn]
  (omit output file → prints to stdout)

JSON spec schema
----------------
{
  "process_id"   : "Proc_1",
  "process_name" : "My Process",
  "executable"   : false,

  "pools": [                          // at least one pool required
    {
      "id"         : "Pool_1",
      "name"       : "My Organization",
      "is_internal": true,            // false → black-box pool (no lanes/elements)
      "lanes": [
        {
          "id"      : "Lane_1",
          "name"    : "Sales",
          "sequence": ["SE_1","T_1","GW_1","T_2","EE_1"]   // L→R order hint
        },
        {
          "id"      : "Lane_2",
          "name"    : "Finance",
          "sequence": ["T_3","EE_2"]
        }
      ]
    },
    {
      "id"         : "Pool_Ext",
      "name"       : "Client",
      "is_internal": false            // black-box: no lanes needed
    }
  ],

  "elements": {
    "SE_1" : {"type": "startEvent",        "name": "Order received",     "eventDef": "message"},
    "T_1"  : {"type": "userTask",          "name": "Validate order"},
    "GW_1" : {"type": "exclusiveGateway",  "name": "Valid?",             "direction": "Diverging", "default": "F_4"},
    "T_2"  : {"type": "userTask",          "name": "Process order"},
    "T_3"  : {"type": "serviceTask",       "name": "Send invoice"},
    "EE_1" : {"type": "endEvent",          "name": "Order rejected",     "eventDef": "none"},
    "EE_2" : {"type": "endEvent",          "name": "Order completed",    "eventDef": "none"},
    "GW_J" : {"type": "exclusiveGateway",  "name": "",                   "direction": "Converging"},
    "BT_1" : {"type": "boundaryEvent",     "name": "3 days",             "eventDef": "timer",
               "attachedTo": "T_1",        "cancelActivity": true}
  },

  "sequence_flows": [
    {"id": "F_1", "source": "SE_1",  "target": "T_1"},
    {"id": "F_2", "source": "T_1",   "target": "GW_1"},
    {"id": "F_3", "source": "GW_1",  "target": "T_2",   "name": "Yes"},
    {"id": "F_4", "source": "GW_1",  "target": "EE_1",  "name": "No",   "isDefault": true},
    {"id": "F_5", "source": "T_2",   "target": "T_3"},
    {"id": "F_6", "source": "T_3",   "target": "EE_2"}
  ],

  "message_flows": [
    {"id": "MF_1", "source": "Pool_Ext", "target": "SE_1", "name": "Purchase Order"}
  ]
}

Notes
-----
- sequence[].sequence is a HINT for left-to-right order within the lane.
  The algorithm does topological sort of sequence_flows and uses the hint
  only to break ties. You do NOT need to list every element; unlisted ones
  are appended at the end.
- boundaryEvent elements must have "attachedTo" set to the host task id.
  They are positioned automatically offset from their host.
- For gateways, "direction" must be "Diverging" or "Converging".
- "default" on a gateway is the ID of the default sequence flow.
- eventDef options: none | message | timer | error | escalation |
                    cancel | compensation | signal | terminate | link | conditional
"""

import json
import sys
import textwrap
from collections import defaultdict, deque
from xml.etree import ElementTree as ET

# ─────────────────────────────────────────────────────────────────────────────
# Layout constants
# ─────────────────────────────────────────────────────────────────────────────
LANE_H          = 180     # height per lane (px)
POOL_LABEL_W    = 30      # pool vertical label band width
LANE_LABEL_W    = 30      # lane vertical label band width
CONTENT_START_X = 200     # X of first element centre (relative to pool left)
H_GAP           = 140     # horizontal centre-to-centre gap between columns
POOL_V_GAP      = 150     # vertical gap between pools
BOUNDARY_OFFSET = 30      # how far boundary events sit below host centre

DIM = {          # (width, height) per element category
    "event":   (36,  36),
    "gateway": (50,  50),
    "task":    (100, 80),
}

# ─────────────────────────────────────────────────────────────────────────────
# Element classification
# ─────────────────────────────────────────────────────────────────────────────
def classify(etype: str) -> str:
    e = etype.lower()
    if "event" in e:
        return "event"
    if "gateway" in e:
        return "gateway"
    return "task"


def dims(etype: str):
    return DIM[classify(etype)]


# ─────────────────────────────────────────────────────────────────────────────
# Topological column assignment  (longest-path labelling)
# ─────────────────────────────────────────────────────────────────────────────
def compute_columns(elem_ids: set, flows: list, hint_order: list) -> dict:
    """
    Returns {elem_id: col_index} where col_index=0 is leftmost.
    Uses longest-path topo sort; hint_order breaks ties for equal-column elems.
    boundary events are excluded — positioned relative to host later.
    """
    succ  = defaultdict(list)
    in_deg = defaultdict(int)

    for f in flows:
        s, t = f["source"], f["target"]
        if s in elem_ids and t in elem_ids:
            succ[s].append(t)
            in_deg[t] += 1

    # seed with elements that have no incoming edges (within this pool)
    col = {}
    hint_pos = {eid: i for i, eid in enumerate(hint_order)}
    roots = sorted(
        [eid for eid in elem_ids if in_deg.get(eid, 0) == 0],
        key=lambda e: hint_pos.get(e, 9999)
    )
    queue = deque(roots)
    for r in roots:
        col[r] = 0

    while queue:
        node = queue.popleft()
        for nxt in succ[node]:
            new_col = col[node] + 1
            if col.get(nxt, -1) < new_col:
                col[nxt] = new_col
            in_deg[nxt] -= 1
            if in_deg[nxt] == 0:
                queue.append(nxt)

    # fill anything not reached (disconnected)
    for eid in elem_ids:
        col.setdefault(eid, 0)

    return col


# ─────────────────────────────────────────────────────────────────────────────
# Position computation
# ─────────────────────────────────────────────────────────────────────────────
def compute_positions(spec: dict):
    """
    Returns:
        positions  : {elem_id: (x, y, w, h)}   absolute coordinates
        pool_boxes : {pool_id: (x, y, w, h)}
        lane_boxes : {lane_id: (x, y, w, h)}
    """
    elements   = spec.get("elements", {})
    pools      = spec.get("pools", [])
    flows      = spec.get("sequence_flows", [])

    positions  = {}
    pool_boxes = {}
    lane_boxes = {}

    # boundary events are positioned relative to host → exclude from topo
    boundary_ids = {
        eid for eid, el in elements.items()
        if el.get("type", "").lower() == "boundaryevent"
    }

    pool_y = 0  # running Y position across pools

    # ── Pre-pass: compute global max width across all internal pools ──────────
    # Black-box pools will use this same width for visual alignment.
    global_total_w = POOL_LABEL_W + 300  # minimum fallback
    for pool in pools:
        if not pool.get("is_internal", True):
            continue
        lanes = pool.get("lanes", [])
        if not lanes:
            continue
        pool_elem_ids_pre = set()
        hint_order_pre    = []
        for lane in lanes:
            for eid in lane.get("sequence", []):
                if eid in elements and eid not in boundary_ids:
                    pool_elem_ids_pre.add(eid)
                    hint_order_pre.append(eid)
        for f in flows:
            for eid in (f["source"], f["target"]):
                if eid in elements and eid not in boundary_ids and eid not in pool_elem_ids_pre:
                    pool_elem_ids_pre.add(eid)
        if pool_elem_ids_pre:
            col_pre   = compute_columns(pool_elem_ids_pre, flows, hint_order_pre)
            max_c     = max(col_pre.values(), default=0)
            w_pre     = POOL_LABEL_W + LANE_LABEL_W + CONTENT_START_X + max_c * H_GAP + 80
            global_total_w = max(global_total_w, w_pre)

    for pool in pools:
        pool_id = pool["id"]
        pool_x  = 0

        if not pool.get("is_internal", True):
            # Black-box pool: same width as the widest internal pool
            pool_boxes[pool_id] = (pool_x, pool_y, global_total_w, LANE_H)
            pool_y += LANE_H + POOL_V_GAP
            continue

        lanes = pool.get("lanes", [])
        if not lanes:
            pool_y += POOL_V_GAP
            continue

        # collect all elements in this pool
        pool_elem_ids = set()
        lane_of = {}        # elem_id → lane_id
        hint_order = []     # flat ordered hint for topo tie-breaking

        for lane in lanes:
            seq = lane.get("sequence", [])
            hint_order.extend(seq)
            for eid in seq:
                if eid in elements and eid not in boundary_ids:
                    pool_elem_ids.add(eid)
                    lane_of[eid] = lane["id"]

        # elements mentioned in flows but not in any lane sequence → assign to first lane
        all_flow_ids = set()
        for f in flows:
            all_flow_ids.update([f["source"], f["target"]])
        for eid in all_flow_ids:
            if eid in elements and eid not in boundary_ids and eid not in pool_elem_ids:
                if lanes:
                    pool_elem_ids.add(eid)
                    lane_of.setdefault(eid, lanes[0]["id"])

        # topo column assignment
        col_of = compute_columns(pool_elem_ids, flows, hint_order)

        # determine per-lane column sequences for vertical centering
        lane_cols = defaultdict(list)   # lane_id → sorted list of col indices used
        for eid, lid in lane_of.items():
            lane_cols[lid].append(col_of[eid])

        # max column across all lanes → total width
        max_col = max((col_of[eid] for eid in pool_elem_ids), default=0)
        total_w = POOL_LABEL_W + LANE_LABEL_W + CONTENT_START_X + max_col * H_GAP + 80

        V_PAD   = 20   # top/bottom padding inside lane
        V_GAP   = 20   # vertical gap between stacked elements

        # lay out lanes top to bottom
        lane_y = pool_y
        for lane in lanes:
            lid    = lane["id"]
            lane_x = pool_x + POOL_LABEL_W

            # Group elements in this lane by column
            col_groups: dict = defaultdict(list)
            for eid, l in lane_of.items():
                if l == lid:
                    col_groups[col_of[eid]].append(eid)

            # Required lane height: worst-case column (most stacked elements)
            # Formula: V_PAD + n*h + (n-1)*V_GAP + V_PAD = 2*V_PAD + n*h + (n-1)*V_GAP
            max_stack_h = 0
            for eids_in_col in col_groups.values():
                n = len(eids_in_col)
                col_h = (2 * V_PAD
                         + sum(dims(elements[eid].get("type","task"))[1] for eid in eids_in_col)
                         + (n - 1) * V_GAP)
                max_stack_h = max(max_stack_h, col_h)

            lane_h = max(LANE_H, max_stack_h)
            lane_boxes[lid] = (lane_x, lane_y, total_w - POOL_LABEL_W, lane_h)

            for col, eids_in_col in col_groups.items():
                cx = lane_x + LANE_LABEL_W + CONTENT_START_X + col * H_GAP
                n  = len(eids_in_col)
                if n == 1:
                    eid   = eids_in_col[0]
                    etype = elements[eid].get("type", "task")
                    w, h  = dims(etype)
                    cy    = lane_y + lane_h // 2
                    positions[eid] = (cx - w // 2, cy - h // 2, w, h)
                else:
                    # Stack top-down with explicit padding — guaranteed no overlap
                    cursor_y = lane_y + V_PAD
                    for eid in eids_in_col:
                        etype = elements[eid].get("type", "task")
                        w, h  = dims(etype)
                        positions[eid] = (cx - w // 2, cursor_y, w, h)
                        cursor_y += h + V_GAP

            lane_y += lane_h

        # Pool height = sum of actual lane heights (not fixed LANE_H)
        pool_h = sum(lane_boxes[lane["id"]][3] for lane in lanes if lane["id"] in lane_boxes)
        pool_boxes[pool_id] = (pool_x, pool_y, total_w, pool_h)
        pool_y += pool_h + POOL_V_GAP

    # position boundary events relative to their host
    # Group by host to handle multiple boundary events on the same task
    boundary_by_host: dict = defaultdict(list)
    for eid, el in elements.items():
        if eid in boundary_ids:
            host_id = el.get("attachedTo", "")
            boundary_by_host[host_id].append(eid)

    for host_id, b_eids in boundary_by_host.items():
        if host_id not in positions:
            for eid in b_eids:
                positions[eid] = (0, 0, *dims(elements[eid].get("type", "boundaryEvent")))
            continue
        hx, hy, hw, hh = positions[host_id]
        n = len(b_eids)
        for idx, eid in enumerate(b_eids):
            bw, bh = dims(elements[eid].get("type", "boundaryEvent"))
            # Distribute horizontally along the bottom edge of the host.
            # Center of each event lies exactly ON the bottom edge (hy+hh).
            slot_w  = hw / (n + 1)
            bx = int(hx + slot_w * (idx + 1) - bw // 2)
            by = hy + hh - bh // 2   # center ON the bottom edge
            positions[eid] = (bx, by, bw, bh)

    return positions, pool_boxes, lane_boxes


# ─────────────────────────────────────────────────────────────────────────────
# XML construction helpers
# ─────────────────────────────────────────────────────────────────────────────
NS_BPMN  = "http://www.omg.org/spec/BPMN/20100524/MODEL"
NS_BPMNDI= "http://www.omg.org/spec/BPMN/20100524/DI"
NS_DC    = "http://www.omg.org/spec/DD/20100524/DC"
NS_DI    = "http://www.omg.org/spec/DD/20100524/DI"

B   = "{%s}" % NS_BPMN
DI  = "{%s}" % NS_BPMNDI
DC  = "{%s}" % NS_DC
DIF = "{%s}" % NS_DI

ET.register_namespace("bpmn",   NS_BPMN)
ET.register_namespace("bpmndi", NS_BPMNDI)
ET.register_namespace("dc",     NS_DC)
ET.register_namespace("di",     NS_DI)


def sub(parent, tag, **attrs):
    return ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})


EVENT_DEF_TAG = {
    "message":      B + "messageEventDefinition",
    "timer":        B + "timerEventDefinition",
    "error":        B + "errorEventDefinition",
    "escalation":   B + "escalationEventDefinition",
    "cancel":       B + "cancelEventDefinition",
    "compensation": B + "compensateEventDefinition",
    "signal":       B + "signalEventDefinition",
    "terminate":    B + "terminateEventDefinition",
    "link":         B + "linkEventDefinition",
    "conditional":  B + "conditionalEventDefinition",
}

TASK_TAG = {
    "task":             B + "task",
    "usertask":         B + "userTask",
    "servicetask":      B + "serviceTask",
    "sendtask":         B + "sendTask",
    "receivetask":      B + "receiveTask",
    "scripttask":       B + "scriptTask",
    "manualtask":       B + "manualTask",
    "businessruletask": B + "businessRuleTask",
    "callactivity":     B + "callActivity",
    "subprocess":       B + "subProcess",
}

GW_TAG = {
    "exclusivegateway":  B + "exclusiveGateway",
    "parallelgateway":   B + "parallelGateway",
    "inclusivegateway":  B + "inclusiveGateway",
    "eventbasedgateway": B + "eventBasedGateway",
    "complexgateway":    B + "complexGateway",
}


def make_element_node(parent, eid: str, el: dict):
    """Add the semantic BPMN element to parent."""
    etype = el.get("type", "task").lower()
    name  = el.get("name", "")
    attrs = {"id": eid}
    if name:
        attrs["name"] = name

    if "gateway" in etype:
        tag = GW_TAG.get(etype, B + "exclusiveGateway")
        direction = el.get("direction", "")
        if direction:
            attrs["gatewayDirection"] = direction
        default_flow = el.get("default")
        if default_flow:
            attrs["default"] = default_flow
        node = sub(parent, tag, **attrs)

    elif "event" in etype:
        if etype == "startevent":
            node = sub(parent, B + "startEvent", **attrs)
        elif etype == "endevent":
            node = sub(parent, B + "endEvent", **attrs)
        elif etype == "boundaryevent":
            cancel = str(el.get("cancelActivity", True)).lower()
            attrs["cancelActivity"] = cancel
            host = el.get("attachedTo", "")
            if host:
                attrs["attachedToRef"] = host
            node = sub(parent, B + "boundaryEvent", **attrs)
        else:
            node = sub(parent, B + "intermediateCatchEvent", **attrs)
        # add event definition child
        edef = el.get("eventDef", "none")
        if edef and edef != "none":
            def_tag = EVENT_DEF_TAG.get(edef.lower())
            if def_tag:
                sub(node, def_tag, id=eid + "_def")
    else:
        tag = TASK_TAG.get(etype, B + "task")
        node = sub(parent, tag, **attrs)

    return node


# ─────────────────────────────────────────────────────────────────────────────
# Port helpers
# ─────────────────────────────────────────────────────────────────────────────
def get_port(box, side: str):
    """Return the (x, y) coordinate of a named port on an element box."""
    x, y, w, h = box
    return {
        "left":   (x,          y + h // 2),
        "right":  (x + w,      y + h // 2),
        "top":    (x + w // 2, y),
        "bottom": (x + w // 2, y + h),
    }[side]


def opposite(side: str) -> str:
    return {"left": "right", "right": "left", "top": "bottom", "bottom": "top"}[side]


def route_orthogonal(src_pt, tgt_pt, src_side: str, tgt_side: str) -> list:
    """
    Generate orthogonal waypoints from src_pt exiting src_side
    to tgt_pt entering tgt_side.  Uses a simple L-shape or Z-shape.
    """
    sx, sy = src_pt
    tx, ty = tgt_pt

    # Direct straight line
    if src_side in ("left", "right") and tgt_side in ("left", "right"):
        mid_x = (sx + tx) // 2
        if sx != tx:
            return [(sx, sy), (mid_x, sy), (mid_x, ty), (tx, ty)]
        return [(sx, sy), (tx, ty)]

    if src_side in ("top", "bottom") and tgt_side in ("left", "right"):
        return [(sx, sy), (sx, ty), (tx, ty)]

    if src_side in ("left", "right") and tgt_side in ("top", "bottom"):
        return [(sx, sy), (tx, sy), (tx, ty)]

    if src_side in ("top", "bottom") and tgt_side in ("top", "bottom"):
        mid_y = (sy + ty) // 2
        return [(sx, sy), (sx, mid_y), (tx, mid_y), (tx, ty)]

    return [(sx, sy), (tx, ty)]


# ─────────────────────────────────────────────────────────────────────────────
# Gateway port assignment  (the core of correct BPMN layout)
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# Port assignment  (gateways + activities — collision-safe)
# ─────────────────────────────────────────────────────────────────────────────
# Priority order: preferred side given relative Y, then fallback sides
EXIT_PREF  = ["right", "bottom", "top",   "left"]
ENTRY_PREF = ["left",  "top",    "bottom", "right"]


def _preferred_exit(src_box, tgt_box) -> str:
    """Natural exit side from src toward tgt, ignoring current usage."""
    dy = (tgt_box[1] + tgt_box[3] // 2) - (src_box[1] + src_box[3] // 2)
    if abs(dy) < LANE_H * 0.4:
        return "right"
    return "bottom" if dy > 0 else "top"


def _preferred_entry(src_box, tgt_box) -> str:
    """Natural entry side of tgt coming from src, ignoring current usage."""
    dy = (tgt_box[1] + tgt_box[3] // 2) - (src_box[1] + src_box[3] // 2)
    if abs(dy) < LANE_H * 0.4:
        return "left"
    return "top" if dy > 0 else "bottom"


def _next_available(preferred: str, pref_list: list, used: set) -> str:
    """Return preferred if free, else the next unused side in pref_list."""
    if preferred not in used:
        return preferred
    for candidate in pref_list:
        if candidate not in used:
            return candidate
    return preferred   # fallback: accept collision rather than crash


def assign_all_ports(elements: dict, flows: list, positions: dict) -> dict:
    """
    Assign physical ports to EVERY flow endpoint (source and target),
    for all element types — gateways, tasks, events.

    Returns port_map: {(flow_id, elem_id): side}
      side ∈ {"left", "right", "top", "bottom"}

    Rules
    ─────
    Gateways — hard constraints first (architectural):
      DIVERGING : all incoming → LEFT; outgoing assigned by relative target Y
      CONVERGING: all outgoing → RIGHT; incoming assigned by relative source Y

    All elements (including gateways, after hard constraints):
      • Used-port registry per element prevents two flows sharing a port.
      • Preferred sides are position-driven; ties broken by priority list.
      • Entries and exits compete for the same 4 ports.

    Assignment order within each element:
      1. Outgoing flows, sorted by natural side (right > bottom > top > left)
      2. Incoming flows, sorted by natural side (left > top > bottom > right)
      This ensures exits claim their preferred sides first (exits are usually
      more predictable); entries adapt to what remains.
    """
    port_map: dict = {}
    used: dict     = {}   # elem_id → set of sides already claimed

    def claim(flow_id, elem_id, side):
        port_map[(flow_id, elem_id)] = side
        used.setdefault(elem_id, set()).add(side)

    # ── Phase 1: hard gateway constraints ────────────────────────────────────
    for eid, el in elements.items():
        if classify(el.get("type", "")) != "gateway":
            continue
        direction = el.get("direction", "Diverging")
        in_flows  = [f for f in flows if f["target"] == eid]
        out_flows = [f for f in flows if f["source"] == eid]

        if direction == "Diverging":
            for f in in_flows:
                claim(f["id"], eid, "left")
        elif direction == "Converging":
            for f in out_flows:
                claim(f["id"], eid, "right")

    # ── Phase 2: position-based assignment with collision avoidance ──────────
    # Process outgoing then incoming per element
    for eid in elements:
        out_flows = [f for f in flows if f["source"] == eid]
        in_flows  = [f for f in flows if f["target"] == eid]

        src_box = positions.get(eid)
        if not src_box:
            continue

        # Sort outgoing by how "natural" the preferred side is
        def exit_priority(f):
            tgt_box = positions.get(f["target"])
            if not tgt_box:
                return 0
            pref = _preferred_exit(src_box, tgt_box)
            return EXIT_PREF.index(pref)

        for f in sorted(out_flows, key=exit_priority):
            if (f["id"], eid) in port_map:
                continue   # already assigned in Phase 1
            tgt_box = positions.get(f["target"])
            pref    = _preferred_exit(src_box, tgt_box) if tgt_box else "right"
            side    = _next_available(pref, EXIT_PREF, used.get(eid, set()))
            claim(f["id"], eid, side)

        # Sort incoming by how natural the preferred entry side is
        def entry_priority(f):
            s_box = positions.get(f["source"])
            if not s_box:
                return 0
            pref = _preferred_entry(s_box, src_box)
            return ENTRY_PREF.index(pref)

        for f in sorted(in_flows, key=entry_priority):
            if (f["id"], eid) in port_map:
                continue   # already assigned in Phase 1
            s_box = positions.get(f["source"])
            pref  = _preferred_entry(s_box, src_box) if s_box else "left"
            side  = _next_available(pref, ENTRY_PREF, used.get(eid, set()))
            claim(f["id"], eid, side)

    return port_map



def build_waypoints(f: dict, elements: dict, positions: dict,
                    port_map: dict) -> list:
    """
    Compute waypoint list for a sequence flow using the pre-computed port_map
    for both source and target — gateways, tasks, and events alike.
    Falls back to position-based inference only if the element is absent from port_map.
    """
    sid, tid = f["source"], f["target"]
    src_box  = positions.get(sid)
    tgt_box  = positions.get(tid)
    if not src_box or not tgt_box:
        return []

    dy = (tgt_box[1] + tgt_box[3] // 2) - (src_box[1] + src_box[3] // 2)

    # ── Source exit side ─────────────────────────────────────────────────────
    if (f["id"], sid) in port_map:
        src_side = port_map[(f["id"], sid)]
    else:
        # fallback: position-based
        if abs(dy) < LANE_H * 0.4:
            src_side = "right"
        elif dy > 0:
            src_side = "bottom"
        else:
            src_side = "top"

    # ── Target entry side ────────────────────────────────────────────────────
    if (f["id"], tid) in port_map:
        tgt_side = port_map[(f["id"], tid)]
    else:
        # fallback: position-based
        if abs(dy) < LANE_H * 0.4:
            tgt_side = "left"
        elif dy > 0:
            tgt_side = "top"
        else:
            tgt_side = "bottom"

    src_pt = get_port(src_box, src_side)
    tgt_pt = get_port(tgt_box, tgt_side)
    return route_orthogonal(src_pt, tgt_pt, src_side, tgt_side)


# ─────────────────────────────────────────────────────────────────────────────
# Main XML builder
# ─────────────────────────────────────────────────────────────────────────────
def build_xml(spec: dict) -> ET.Element:
    proc_id   = spec.get("process_id", "Process_1")
    proc_name = spec.get("process_name", "Process")
    executable= str(spec.get("executable", False)).lower()
    elements  = spec.get("elements", {})
    pools     = spec.get("pools", [])
    flows     = spec.get("sequence_flows", [])
    msg_flows = spec.get("message_flows", [])

    positions, pool_boxes, lane_boxes = compute_positions(spec)

    # Pre-compute gateway port assignments BEFORE rendering any edges
    port_map = assign_all_ports(elements, flows, positions)

    # ── root ─────────────────────────────────────────────────────────────────
    root = ET.Element(B + "definitions", {
        "id":          "Definitions_1",
        "targetNamespace": "http://bpmn.io/schema/bpmn",
    })

    # ── collaboration ─────────────────────────────────────────────────────────
    collab = sub(root, B + "collaboration", id="Collab_1")
    for pool in pools:
        p_attrs = {"id": pool["id"], "name": pool.get("name", ""), "processRef": proc_id}
        if not pool.get("is_internal", True):
            p_attrs["processRef"] = pool["id"] + "_Proc"
        sub(collab, B + "participant", **p_attrs)

    for mf in msg_flows:
        sub(collab, B + "messageFlow",
            id=mf["id"], name=mf.get("name", ""),
            sourceRef=mf["source"], targetRef=mf["target"])

    # ── process ───────────────────────────────────────────────────────────────
    proc = sub(root, B + "process",
               id=proc_id, name=proc_name, isExecutable=executable)

    # laneSet
    internal_pools = [p for p in pools if p.get("is_internal", True)]
    if internal_pools and any(p.get("lanes") for p in internal_pools):
        lane_set = sub(proc, B + "laneSet", id="LaneSet_1")
        for pool in internal_pools:
            for lane in pool.get("lanes", []):
                lane_el = sub(lane_set, B + "lane",
                              id=lane["id"], name=lane.get("name", ""))
                # gather elements in this lane
                seq = lane.get("sequence", [])
                for eid in seq:
                    if eid in elements:
                        sub(lane_el, B + "flowNodeRef").text = eid
                # boundary events whose host is in this lane
                for eid, el in elements.items():
                    if el.get("type", "").lower() == "boundaryevent":
                        host = el.get("attachedTo", "")
                        if host in seq:
                            sub(lane_el, B + "flowNodeRef").text = eid

    # semantic elements
    boundary_ids = {
        eid for eid, el in elements.items()
        if el.get("type", "").lower() == "boundaryevent"
    }
    # non-boundary first, then boundary (must come after hosts)
    for eid, el in elements.items():
        if eid not in boundary_ids:
            make_element_node(proc, eid, el)
    for eid, el in elements.items():
        if eid in boundary_ids:
            make_element_node(proc, eid, el)

    # sequence flows
    for f in flows:
        sf_attrs = {"id": f["id"], "sourceRef": f["source"], "targetRef": f["target"]}
        if f.get("name"):
            sf_attrs["name"] = f["name"]
        sf = sub(proc, B + "sequenceFlow", **sf_attrs)
        if f.get("condition") and not f.get("isDefault"):
            cond = sub(sf, B + "conditionExpression")
            cond.text = f["condition"]

    # black-box processes
    for pool in pools:
        if not pool.get("is_internal", True):
            sub(root, B + "process",
                id=pool["id"] + "_Proc", isExecutable="false")

    # ── diagram ───────────────────────────────────────────────────────────────
    diagram = sub(root, DI + "BPMNDiagram", id="Diagram_1")
    plane   = sub(diagram, DI + "BPMNPlane", id="Plane_1",
                  bpmnElement="Collab_1")

    # pool and lane shapes
    # Order: lanes first, then pool — renderers paint in XML order (painter's algorithm).
    # Pool written last so it acts as a background frame without covering lane contents.
    for pool in pools:
        pid = pool["id"]
        if pid not in pool_boxes:
            continue
        px, py, pw, ph = pool_boxes[pid]

        # ── lane shapes first ────────────────────────────────────────────────
        for lane in pool.get("lanes", []):
            lid = lane["id"]
            if lid not in lane_boxes:
                continue
            lx, ly, lw, lh = lane_boxes[lid]
            ls = sub(plane, DI + "BPMNShape", id=lid + "_di",
                     bpmnElement=lid, isHorizontal="true")
            sub(ls, DC + "Bounds", x=str(lx), y=str(ly), width=str(lw), height=str(lh))
            if lane.get("name"):
                lbl = sub(ls, DI + "BPMNLabel")
                sub(lbl, DC + "Bounds",
                    x=str(lx), y=str(ly),
                    width=str(LANE_LABEL_W), height=str(lh))

        # ── pool shape last ──────────────────────────────────────────────────
        shape = sub(plane, DI + "BPMNShape", id=pid + "_di",
                    bpmnElement=pid, isHorizontal="true")
        sub(shape, DC + "Bounds", x=str(px), y=str(py), width=str(pw), height=str(ph))
        if pool.get("name"):
            label = sub(shape, DI + "BPMNLabel")
            sub(label, DC + "Bounds", x=str(px), y=str(py),
                width=str(POOL_LABEL_W), height=str(ph))

    # element shapes
    for eid, el in elements.items():
        if eid not in positions:
            continue
        ex, ey, ew, eh = positions[eid]
        etype = el.get("type", "task").lower()
        is_boundary = etype == "boundaryevent"

        sh_attrs = {"id": eid + "_di", "bpmnElement": eid}
        if is_boundary:
            sh_attrs["cancelActivity"] = str(el.get("cancelActivity", True)).lower()
        # XOR gateway must show its X marker explicitly
        if etype == "exclusivegateway":
            sh_attrs["isMarkerVisible"] = "true"

        shape = sub(plane, DI + "BPMNShape", **sh_attrs)
        sub(shape, DC + "Bounds", x=str(ex), y=str(ey), width=str(ew), height=str(eh))

        name = el.get("name", "")
        if name:
            label = sub(shape, DI + "BPMNLabel")
            cat = classify(etype)
            if cat == "task":
                # Label inside the task rectangle
                sub(label, DC + "Bounds",
                    x=str(ex), y=str(ey), width=str(ew), height=str(eh))
            else:
                # Events and gateways: label below the shape
                sub(label, DC + "Bounds",
                    x=str(ex - 10), y=str(ey + eh + 5),
                    width=str(ew + 20), height=str(14))

    # edge shapes (sequence flows)
    for f in flows:
        sid, tid = f["source"], f["target"]
        if sid not in positions or tid not in positions:
            continue
        wpts = build_waypoints(f, elements, positions, port_map)
        if not wpts:
            continue

        edge = sub(plane, DI + "BPMNEdge", id=f["id"] + "_di", bpmnElement=f["id"])
        for wx, wy in wpts:
            sub(edge, DIF + "waypoint", x=str(wx), y=str(wy))
        if f.get("name"):
            label = sub(edge, DI + "BPMNLabel")
            mx = (wpts[0][0] + wpts[-1][0]) // 2
            my = (wpts[0][1] + wpts[-1][1]) // 2
            sub(label, DC + "Bounds", x=str(mx), y=str(my), width=str(50), height=str(14))

    # message flow edges
    for mf in msg_flows:
        src_id, tgt_id = mf["source"], mf["target"]
        # source/target may be pool ids (for black-box) or element ids
        src_box = positions.get(src_id) or pool_boxes.get(src_id)
        tgt_box = positions.get(tgt_id) or pool_boxes.get(tgt_id)
        if not src_box or not tgt_box:
            continue
        edge = sub(plane, DI + "BPMNEdge", id=mf["id"] + "_di", bpmnElement=mf["id"])
        sx, sy = get_port(src_box, "right")
        tx, ty = get_port(tgt_box, "left")
        sub(edge, DIF + "waypoint", x=str(sx), y=str(sy))
        sub(edge, DIF + "waypoint", x=str(tx), y=str(ty))

    return root


# ─────────────────────────────────────────────────────────────────────────────
# Pretty-print XML
# ─────────────────────────────────────────────────────────────────────────────
def indent_xml(elem, level=0):
    """In-place pretty print."""
    pad = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = pad + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = pad
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = pad
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = pad


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        spec = json.load(f)

    root = build_xml(spec)
    indent_xml(root)
    tree = ET.ElementTree(root)

    output = sys.argv[2] if len(sys.argv) > 2 else None
    if output:
        tree.write(output, xml_declaration=True, encoding="UTF-8")
        print(f"[bpmn_layout] ✓ Written: {output}", file=sys.stderr)
    else:
        ET.dump(root)


if __name__ == "__main__":
    main()
