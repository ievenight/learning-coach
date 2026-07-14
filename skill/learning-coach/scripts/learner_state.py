#!/usr/bin/env python3
"""Portable, append-only learner state for the learning-coach skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
TOPIC_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
CHALLENGES = {"exposure", "recall", "explain", "discriminate", "apply", "transfer"}
OUTCOMES = {"success", "partial", "failure", "not_attempted"}
ASSISTANCE = {"none", "prompt", "hint", "worked_example"}
DELAYS = {"immediate", "delayed"}
STATUS_ORDER = ["unseen", "exposed", "assisted", "independent", "delayed", "transfer"]


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    temp.replace(path)


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return rows


def topic_dir(root: Path, topic: str) -> Path:
    if not TOPIC_RE.fullmatch(topic):
        raise ValueError("topic must use lowercase letters, digits, and hyphens")
    return root / "topics" / topic


def load_contract(root: Path, topic: str) -> dict[str, Any]:
    path = topic_dir(root, topic) / "contract.json"
    if not path.exists():
        raise ValueError(f"unknown topic: {topic}")
    return read_json(path)


def update_index(root: Path, contract: dict[str, Any]) -> None:
    path = root / "index.json"
    index = read_json(path) if path.exists() else {"schema_version": SCHEMA_VERSION, "topics": {}}
    topic = contract["topic_id"]
    index["topics"][topic] = {
        "path": f"topics/{topic}",
        "title": contract["title"],
        "updated_at": contract["updated_at"],
    }
    write_json(path, index)


def derive_status(event: dict[str, Any]) -> str | None:
    if event["outcome"] != "success":
        return None
    if event["challenge_type"] == "exposure":
        return "exposed"
    if event["assistance"] != "none":
        return "assisted"
    if event["challenge_type"] == "transfer":
        return "transfer"
    if event["delay_class"] == "delayed":
        return "delayed"
    return "independent"


def rebuild(root: Path, topic: str) -> dict[str, Any]:
    directory = topic_dir(root, topic)
    contract = load_contract(root, topic)
    events = read_jsonl(directory / "evidence.jsonl")
    concepts: dict[str, dict[str, Any]] = {}

    for event in events:
        concept_id = event["concept_id"]
        concept = concepts.setdefault(
            concept_id,
            {
                "status": "unseen",
                "evidence_ids": [],
                "last_checked_at": None,
                "current_signal": None,
                "needs_review": False,
            },
        )
        concept["evidence_ids"].append(event["id"])
        concept["last_checked_at"] = event["ts"]
        concept["current_signal"] = {
            "outcome": event["outcome"],
            "assistance": event["assistance"],
            "challenge_type": event["challenge_type"],
        }
        candidate = derive_status(event)
        if candidate and STATUS_ORDER.index(candidate) > STATUS_ORDER.index(concept["status"]):
            concept["status"] = candidate
        concept["needs_review"] = event["outcome"] in {"partial", "failure"}

    existing = directory / "snapshot.json"
    checkpoint = {"summary": "", "next_move": ""}
    if existing.exists():
        checkpoint = read_json(existing).get("checkpoint", checkpoint)

    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "topic_id": topic,
        "title": contract["title"],
        "goal": contract["goal"],
        "depth": contract.get("depth", ""),
        "current_position": contract.get("current_position", ""),
        "concepts": concepts,
        "checkpoint": checkpoint,
        "updated_at": now(),
    }
    write_json(directory / "snapshot.json", snapshot)
    return snapshot


def command_init(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    directory = topic_dir(root, args.topic)
    if directory.exists():
        raise ValueError(f"topic already exists: {args.topic}")
    timestamp = now()
    contract = {
        "schema_version": SCHEMA_VERSION,
        "topic_id": args.topic,
        "title": args.title,
        "goal": args.goal,
        "depth": args.depth,
        "constraints": [],
        "roadmap": [],
        "current_position": "",
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    write_json(directory / "contract.json", contract)
    (directory / "evidence.jsonl").touch()
    (directory / "interventions.jsonl").touch()
    write_json(directory / "review-queue.json", {"schema_version": SCHEMA_VERSION, "items": []})
    update_index(root, contract)
    rebuild(root, args.topic)
    print(directory)


def command_record(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    directory = topic_dir(root, args.topic)
    load_contract(root, args.topic)
    event = {
        "id": "ev_" + uuid.uuid4().hex[:16],
        "ts": now(),
        "concept_id": args.concept,
        "challenge_type": args.challenge,
        "delay_class": args.delay,
        "outcome": args.outcome,
        "assistance": args.assistance,
        "observation": args.observation,
        "supersedes": args.supersedes,
    }
    append_jsonl(directory / "evidence.jsonl", event)
    rebuild(root, args.topic)
    print(event["id"])


def command_intervene(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    directory = topic_dir(root, args.topic)
    load_contract(root, args.topic)
    event = {
        "id": "in_" + uuid.uuid4().hex[:16],
        "ts": now(),
        "concept_id": args.concept,
        "representation": args.representation,
        "result": args.result,
        "note": args.note,
    }
    append_jsonl(directory / "interventions.jsonl", event)
    print(event["id"])


def command_review(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    directory = topic_dir(root, args.topic)
    load_contract(root, args.topic)
    path = directory / "review-queue.json"
    queue = read_json(path)
    item = {
        "id": "rv_" + uuid.uuid4().hex[:16],
        "concept_id": args.concept,
        "due": args.due,
        "evidence_type": args.evidence_type,
        "prompt": args.prompt,
        "created_at": now(),
    }
    queue["items"] = [x for x in queue["items"] if x["concept_id"] != args.concept]
    queue["items"].append(item)
    queue["items"].sort(key=lambda value: value["due"])
    write_json(path, queue)
    print(item["id"])


def command_checkpoint(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    directory = topic_dir(root, args.topic)
    snapshot = rebuild(root, args.topic)
    snapshot["checkpoint"] = {"summary": args.summary, "next_move": args.next_move}
    snapshot["updated_at"] = now()
    write_json(directory / "snapshot.json", snapshot)
    contract = load_contract(root, args.topic)
    contract["updated_at"] = snapshot["updated_at"]
    write_json(directory / "contract.json", contract)
    update_index(root, contract)


def command_status(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    directory = topic_dir(root, args.topic)
    result = {
        "contract": load_contract(root, args.topic),
        "snapshot": read_json(directory / "snapshot.json"),
        "reviews": read_json(directory / "review-queue.json"),
        "recent_interventions": read_jsonl(directory / "interventions.jsonl")[-5:],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


def command_due(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    target = date.fromisoformat(args.on or date.today().isoformat())
    index_path = root / "index.json"
    if not index_path.exists():
        print("[]")
        return
    due: list[dict[str, Any]] = []
    for topic in read_json(index_path)["topics"]:
        path = topic_dir(root, topic) / "review-queue.json"
        for item in read_json(path)["items"]:
            if date.fromisoformat(item["due"]) <= target:
                due.append({"topic_id": topic, **item})
    due.sort(key=lambda item: (item["due"], item["topic_id"]))
    print(json.dumps(due, ensure_ascii=False, indent=2, sort_keys=True))


def validate_topic(root: Path, topic: str) -> list[str]:
    errors: list[str] = []
    directory = topic_dir(root, topic)
    required = ["contract.json", "evidence.jsonl", "interventions.jsonl", "review-queue.json", "snapshot.json"]
    for name in required:
        if not (directory / name).exists():
            errors.append(f"{topic}: missing {name}")
    if errors:
        return errors
    try:
        contract = read_json(directory / "contract.json")
        if contract.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"{topic}: unsupported contract schema")
        if contract.get("topic_id") != topic:
            errors.append(f"{topic}: contract topic mismatch")
        for event in read_jsonl(directory / "evidence.jsonl"):
            if event.get("challenge_type") not in CHALLENGES:
                errors.append(f"{topic}: invalid challenge in {event.get('id')}")
            if event.get("outcome") not in OUTCOMES:
                errors.append(f"{topic}: invalid outcome in {event.get('id')}")
            if event.get("assistance") not in ASSISTANCE:
                errors.append(f"{topic}: invalid assistance in {event.get('id')}")
            if event.get("delay_class") not in DELAYS:
                errors.append(f"{topic}: invalid delay in {event.get('id')}")
        read_jsonl(directory / "interventions.jsonl")
        queue = read_json(directory / "review-queue.json")
        for item in queue.get("items", []):
            date.fromisoformat(item["due"])
        snapshot = read_json(directory / "snapshot.json")
        for concept in snapshot.get("concepts", {}).values():
            if concept.get("status") not in STATUS_ORDER:
                errors.append(f"{topic}: invalid snapshot status")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"{topic}: {exc}")
    return errors


def command_validate(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    topics = [args.topic] if args.topic else list(read_json(root / "index.json").get("topics", {}))
    errors: list[str] = []
    for topic in topics:
        errors.extend(validate_topic(root, topic))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit(1)
    print(f"valid: {len(topics)} topic(s)")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init")
    init.add_argument("--root", required=True)
    init.add_argument("--topic", required=True)
    init.add_argument("--title", required=True)
    init.add_argument("--goal", required=True)
    init.add_argument("--depth", default="")
    init.set_defaults(func=command_init)

    record = commands.add_parser("record")
    record.add_argument("--root", required=True)
    record.add_argument("--topic", required=True)
    record.add_argument("--concept", required=True)
    record.add_argument("--challenge", choices=sorted(CHALLENGES), required=True)
    record.add_argument("--outcome", choices=sorted(OUTCOMES), required=True)
    record.add_argument("--assistance", choices=sorted(ASSISTANCE), required=True)
    record.add_argument("--delay", choices=sorted(DELAYS), default="immediate")
    record.add_argument("--observation", required=True)
    record.add_argument("--supersedes")
    record.set_defaults(func=command_record)

    intervention = commands.add_parser("intervene")
    intervention.add_argument("--root", required=True)
    intervention.add_argument("--topic", required=True)
    intervention.add_argument("--concept", required=True)
    intervention.add_argument("--representation", required=True)
    intervention.add_argument("--result", choices=["helped", "no_progress", "unknown"], required=True)
    intervention.add_argument("--note", default="")
    intervention.set_defaults(func=command_intervene)

    review = commands.add_parser("review")
    review.add_argument("--root", required=True)
    review.add_argument("--topic", required=True)
    review.add_argument("--concept", required=True)
    review.add_argument("--due", required=True)
    review.add_argument("--evidence-type", choices=sorted(CHALLENGES - {"exposure"}), required=True)
    review.add_argument("--prompt", required=True)
    review.set_defaults(func=command_review)

    checkpoint = commands.add_parser("checkpoint")
    checkpoint.add_argument("--root", required=True)
    checkpoint.add_argument("--topic", required=True)
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--next-move", required=True)
    checkpoint.set_defaults(func=command_checkpoint)

    status = commands.add_parser("status")
    status.add_argument("--root", required=True)
    status.add_argument("--topic", required=True)
    status.set_defaults(func=command_status)

    due = commands.add_parser("due")
    due.add_argument("--root", required=True)
    due.add_argument("--on")
    due.set_defaults(func=command_due)

    rebuild_command = commands.add_parser("rebuild")
    rebuild_command.add_argument("--root", required=True)
    rebuild_command.add_argument("--topic", required=True)
    rebuild_command.set_defaults(func=lambda args: print(json.dumps(rebuild(Path(args.root).expanduser().resolve(), args.topic), ensure_ascii=False, indent=2)))

    validate = commands.add_parser("validate")
    validate.add_argument("--root", required=True)
    validate.add_argument("--topic")
    validate.set_defaults(func=command_validate)
    return root


def main() -> None:
    args = parser().parse_args()
    try:
        args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()

