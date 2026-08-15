"""Minimal local read-only MCP surface for AI LegalFlow MX source records."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .objects import load_objects
from .sources import temporal_status


TOOLS = [
    {
        "name": "legalflow_sources",
        "description": "List source locks already stored in a local AI LegalFlow MX matter. Read-only; does not search the web or determine legal validity.",
        "inputSchema": {"type": "object", "properties": {"matter": {"type": "string", "description": "Absolute path to the matter"}}, "required": ["matter"]},
    },
    {
        "name": "legalflow_temporal_check",
        "description": "Classify a locked source against a date. Returns a candidate only and requires human legal review.",
        "inputSchema": {"type": "object", "properties": {"matter": {"type": "string"}, "authority": {"type": "string"}, "date": {"type": "string", "description": "YYYY-MM-DD"}}, "required": ["matter", "authority", "date"]},
    },
]


def _text(value: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, indent=2)}]}


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    request_id = request.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"protocolVersion": "2024-11-05", "serverInfo": {"name": "legalflow-mx", "version": "0.1.0"}, "capabilities": {"tools": {}}}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = request.get("params", {})
        arguments = params.get("arguments", {})
        try:
            matter = Path(arguments["matter"])
            objects = load_objects(matter)
            if params.get("name") == "legalflow_sources":
                sources = [{"id": item["id"], "title": item.get("title"), "url": item.get("source", {}).get("url"), "official_status": item.get("official_status"), "verification": item.get("verification"), "temporal": item.get("temporal")} for item in objects["authority"]]
                result = _text({"sources": sources, "notice": "Read-only local source locks. Review legal validity independently."})
            elif params.get("name") == "legalflow_temporal_check":
                authority = next((item for item in objects["authority"] if item["id"] == arguments["authority"]), None)
                if authority is None:
                    raise ValueError("Authority not found in this matter")
                result = _text({"authority": authority["id"], "date": arguments["date"], "result": temporal_status(authority, arguments["date"]), "notice": "Candidate only; human legal review required."})
            else:
                raise ValueError("Unknown tool")
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except (KeyError, ValueError, OSError) as error:
            return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": str(error)}], "isError": True}}
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}


def main() -> int:
    for line in sys.stdin:
        try:
            response = handle_request(json.loads(line))
            if response is not None:
                print(json.dumps(response, ensure_ascii=False), flush=True)
        except json.JSONDecodeError:
            print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
