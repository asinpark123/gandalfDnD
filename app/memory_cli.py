"""Bounded operational commands for M4 source backfill and index recovery."""

from __future__ import annotations

import argparse
import json
import socket
import uuid
from dataclasses import asdict, is_dataclass

from app.config import get_settings
from app.db import get_session_factory
from app.embeddings import DeterministicEmbeddingProvider, LocalFastEmbedProvider
from app.memory import (
    drain_index_jobs,
    ensure_embedding_profile,
    project_completed_turns,
    recover_expired_leases,
    start_index_build,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GandalfDnD memory index maintenance")
    parser.add_argument("--provider", choices=("deterministic", "local"), default="local")
    parser.add_argument("--dimensions", type=int, default=64)
    subcommands = parser.add_subparsers(dest="command", required=True)
    backfill = subcommands.add_parser("backfill", help="project eligible completed turns")
    backfill.add_argument("--campaign-id", type=uuid.UUID)
    backfill.add_argument("--limit", type=int, default=100)
    build = subcommands.add_parser("build", help="create/recover a campaign profile build")
    build.add_argument("campaign_id", type=uuid.UUID)
    drain = subcommands.add_parser("drain", help="process a bounded number of durable jobs")
    drain.add_argument("--limit", type=int, default=25)
    subcommands.add_parser("recover", help="release expired job leases")
    return parser


def _provider(args: argparse.Namespace) -> DeterministicEmbeddingProvider | LocalFastEmbedProvider:
    return (
        DeterministicEmbeddingProvider(dimensions=args.dimensions)
        if args.provider == "deterministic"
        else LocalFastEmbedProvider(get_settings().embedding_model_dir)
    )


def main() -> None:
    args = _parser().parse_args()
    factory = get_session_factory()
    if args.command == "backfill":
        with factory() as session:
            result = project_completed_turns(
                session, campaign_id=args.campaign_id, limit=args.limit
            )
            session.commit()
    elif args.command == "build":
        provider = _provider(args)
        with factory() as session:
            profile = ensure_embedding_profile(session, provider)
            index = start_index_build(session, campaign_id=args.campaign_id, profile_id=profile.id)
            session.commit()
            result = {"index_id": str(index.id), "status": index.status}
    elif args.command == "drain":
        provider = _provider(args)
        result = drain_index_jobs(
            provider=provider,
            worker_id=f"cli:{socket.gethostname()}",
            limit=args.limit,
        )
    elif args.command == "recover":
        with factory() as session:
            result = {"recovered": recover_expired_leases(session)}
            session.commit()
    else:
        raise AssertionError(f"unsupported memory command: {args.command}")
    print(json.dumps(asdict(result) if is_dataclass(result) else result, default=str))


if __name__ == "__main__":
    main()
