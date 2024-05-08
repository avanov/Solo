import argparse
from typing import Dict, Any, Optional, List

from alembic import command as alembic_cmd
from .config import alembic_config_from_solo


ALEMBIC_KV_OPTS = {  # Copied from alembic.config.CommandLine
    'template': (
        "-t", "--template",
        dict(
            default='generic',
            type=str,
            help="Setup template for use with 'init'"
        )
    ),
    'message': (
        "-m", "--message",
        dict(
            type=str,
            help="Message string to use with 'revision'")
    ),
    'sql': (
        "--sql",
        dict(
            action="store_true",
            help="Don't emit SQL to database - dump to "
            "standard output/file instead"
        )
    ),
    'tag': (
        "--tag",
        dict(
            type=str,
            help="Arbitrary 'tag' name - can be used by "
            "custom env.py scripts.")
    ),
    'head': (
        "--head",
        dict(
            type=str,
            help="Specify head revision or <branchname>@head "
            "to base new revision on."
        )
    ),
    'splice': (
        "--splice",
        dict(
            action="store_true",
            help="Allow a non-head revision as the "
            "'head' to splice onto"
        )
    ),
    'depends_on': (
        "--depends-on",
        dict(
            action="append",
            help="Specify one or more revision identifiers "
            "which this revision should depend on."
        )
    ),
    'rev_id': (
        "--rev-id",
        dict(
            type=str,
            help="Specify a hardcoded revision id instead of "
            "generating one"
        )
    ),
    'version_path': (
        "--version-path",
        dict(
            type=str,
            help="Specify specific path from config for "
            "version file"
        )
    ),
    'branch_label': (
        "--branch-label",
        dict(
            type=str,
            help="Specify a branch label to apply to the "
            "new revision"
        )
    ),
    'verbose': (
        "-v", "--verbose",
        dict(
            action="store_true",
            help="Use more verbose output"
        )
    ),
    'resolve_dependencies': (
        '--resolve-dependencies',
        dict(
            action="store_true",
            help="Treat dependency versions as down revisions"
        )
    ),
    'autogenerate': (
        "--autogenerate",
        dict(
            action="store_true",
            help="Populate revision script with candidate "
            "migration operations, based on comparison "
            "of database to model.")
    ),
    'head_only': (
        "--head-only",
        dict(
            action="store_true",
            help="Deprecated.  Use --verbose for "
            "additional output")
    ),
    'rev_range': (
        "-r", "--rev-range",
        dict(
            action="store",
            help="Specify a revision range; "
            "format is [start]:[end]")
    )
}

ALEMBIC_POS_OPTS = {  # Copied from alembic.config.CommandLine
    'directory': "location of scripts directory",
    'revision': "revision identifier",
    'revisions': "one or more revisions, or 'heads' for all heads"

}


def integrate_alembic_cli(parent_cli: argparse._SubParsersAction, prefix: str = 'db') -> None:
    """
    """
    db = parent_cli.add_parser(prefix, help='Database commands integrated with Alembic CLI')
    subparsers = db.add_subparsers(title='sub-commands',
                                   description='valid sub-commands',
                                   help='Available Alembic commands',
                                   dest='sub-command')
    subparsers.required = True

    # Branches
    # http://alembic.readthedocs.io/en/latest/api/commands.html#alembic.command.branches
    # ----------------------------------------------------------------------------------
    branches = subparsers.add_parser('branches', help='Integrates "alembic branches" command. '
                                                      'Shows current branch points.')
    branches = _populate_subparser(branches, ['verbose'])
    branches.set_defaults(func=branches_cmd)

    # Current
    # http://alembic.readthedocs.io/en/latest/api/commands.html#alembic.command.current
    # ----------------------------------------------------------------------------------
    current = subparsers.add_parser('current', help='Integrates "alembic current" command. '
                                                    'Displays the current revision for a database.')
    current = _populate_subparser(current, ['verbose', 'head_only'])
    current.set_defaults(func=current_cmd)

    # Downgrade
    # http://alembic.readthedocs.io/en/latest/api/commands.html#alembic.command.downgrade
    # ----------------------------------------------------------------------------------
    downgrade = subparsers.add_parser('downgrade', help='Integrates "alembic downgrade" command. '
                                                        'Reverts to a previous version.')
    downgrade = _populate_subparser(downgrade, ['sql', 'tag'], ['revision'])
    downgrade.set_defaults(func=downgrade_cmd)

    # Edit
    # http://alembic.readthedocs.io/en/latest/api/commands.html#alembic.command.edit
    # ----------------------------------------------------------------------------------
    edit = subparsers.add_parser('edit', help='Integrates "alembic edit" command. '
                                              'Edit revision script(s) using $EDITOR.')
    edit = _populate_subparser(edit, pos_opts=['revision'])
    edit.set_defaults(func=edit_cmd)

    # Heads
    # http://alembic.readthedocs.io/en/latest/api/commands.html#alembic.command.heads
    # ----------------------------------------------------------------------------------
    heads = subparsers.add_parser('heads', help='Integrates "alembic heads" command. '
                                                'Shows current available heads in the script directory.')
    heads = _populate_subparser(heads, ['verbose', 'resolve_dependencies'])
    heads.set_defaults(func=heads_cmd)

    # History
    # http://alembic.readthedocs.io/en/latest/api/commands.html#alembic.command.history
    # ----------------------------------------------------------------------------------
    history = subparsers.add_parser('history', help='Integrates "alembic history" command. '
                                                    'List changeset scripts in chronological order.')
    history = _populate_subparser(history, ['rev_range', 'verbose'])
    history.set_defaults(func=history_cmd)

    # List templates
    # http://alembic.readthedocs.io/en/latest/api/commands.html#alembic.command.list_templates
    # ----------------------------------------------------------------------------------
    list_templates = subparsers.add_parser('list_templates',
                                           help='Integrates "alembic list_templates" command. '
                                                'List available templates.')
    list_templates.set_defaults(func=list_templates_cmd)

    # Merge
    # http://alembic.readthedocs.io/en/latest/api/commands.html#alembic.command.merge
    # ----------------------------------------------------------------------------------
    merge = subparsers.add_parser('merge', help='Integrates "alembic merge" command. '
                                                'Merges two revisions together. Creates a new migration file.')
    merge = _populate_subparser(merge, ['message', 'branch_label', 'rev_id'], ['revisions'])
    merge.set_defaults(func=merge_cmd)

    # Revision
    # http://alembic.readthedocs.io/en/latest/api/commands.html#alembic.command.revision
    # ----------------------------------------------------------------------------------
    revision = subparsers.add_parser('revision', help='Integrates "alembic revision" command. '
                                                      'Creates a new revision file.')
    revision = _populate_subparser(revision,
        ['message', 'autogenerate', 'sql', 'head', 'splice', 'branch_label', 'rev_id', 'depends_on'])
    revision.set_defaults(func=revision_cmd)

    # Show
    # http://alembic.readthedocs.io/en/latest/api/commands.html#alembic.command.show
    # ----------------------------------------------------------------------------------
    show = subparsers.add_parser('show', help='Integrates "alembic show" command. '
                                              'Show the revision(s) denoted by the given symbol.')
    show = _populate_subparser(show, pos_opts=['revision'])
    show.set_defaults(func=show_cmd)

    # Stamp
    # http://alembic.readthedocs.io/en/latest/api/commands.html#alembic.command.stamp
    # ----------------------------------------------------------------------------------
    stamp = subparsers.add_parser('stamp', help='Integrates "alembic stamp" command. '
                                                'Stamp the revision table with the given revision; don’t run any migrations.')
    stamp = _populate_subparser(stamp, ['sql', 'tag'], ['revision'])
    stamp.set_defaults(func=stamp_cmd)

    # Upgrade
    # http://alembic.readthedocs.io/en/latest/api/commands.html#alembic.command.upgrade
    # ----------------------------------------------------------------------------------
    upgrade = subparsers.add_parser('upgrade', help='Integrates "alembic upgrade" command. '
                                                    'Upgrades to a later version.')
    upgrade = _populate_subparser(upgrade, ['sql', 'tag'], ['revision'])
    upgrade.set_defaults(func=upgrade_cmd)


def upgrade_cmd(args, solo_cfg: Dict[str, Any]):
    config = alembic_config_from_solo(solo_cfg)
    alembic_cmd.upgrade(config, revision=args.revision, sql=args.sql, tag=args.tag)


def revision_cmd(args, solo_cfg: Dict[str, Any]):
    config = alembic_config_from_solo(solo_cfg)
    alembic_cmd.revision(config,
                         message=args.message,
                         autogenerate=args.autogenerate,
                         sql=args.sql,
                         head=args.head,
                         splice=args.splice,
                         branch_label=args.branch_label,
                         version_path=None,
                         rev_id=args.rev_id,
                         depends_on=args.depends_on)


def heads_cmd(args, solo_cfg: Dict[str, Any]):
    config = alembic_config_from_solo(solo_cfg)
    alembic_cmd.heads(config, verbose=args.verbose, resolve_dependencies=args.resolve_dependencies)


def history_cmd(args, solo_cfg: Dict[str, Any]):
    config = alembic_config_from_solo(solo_cfg)
    alembic_cmd.history(config, verbose=args.verbose, rev_range=args.rev_range)


def list_templates_cmd(args, solo_cfg: Dict[str, Any]):
    config = alembic_config_from_solo(solo_cfg)
    alembic_cmd.list_templates(config)


def merge_cmd(args, solo_cfg: Dict[str, Any]):
    config = alembic_config_from_solo(solo_cfg)
    alembic_cmd.merge(config,
                      revisions=args.revisions,
                      message=args.message,
                      branch_label=args.branch_label,
                      rev_id=args.rev_id)


def show_cmd(args, solo_cfg: Dict[str, Any]):
    config = alembic_config_from_solo(solo_cfg)
    alembic_cmd.show(config, rev=args.revision)


def stamp_cmd(args, solo_cfg: Dict[str, Any]):
    config = alembic_config_from_solo(solo_cfg)
    alembic_cmd.stamp(config, revision=args.revision, sql=args.sql, tag=args.tag)


def branches_cmd(args, solo_cfg: Dict[str, Any]):
    config = alembic_config_from_solo(solo_cfg)
    alembic_cmd.branches(config, verbose=args.verbose)


def current_cmd(args, solo_cfg: Dict[str, Any]):
    config = alembic_config_from_solo(solo_cfg)
    alembic_cmd.current(config, verbose=args.verbose, head_only=args.head_only)


def downgrade_cmd(args, solo_cfg: Dict[str, Any]):
    config = alembic_config_from_solo(solo_cfg)
    alembic_cmd.downgrade(config, revision=args.revision, sql=args.sql, tag=args.tag)


def edit_cmd(args, solo_cfg: Dict[str, Any]):
    config = alembic_config_from_solo(solo_cfg)
    alembic_cmd.edit(config, rev=args.revision)


def _populate_subparser(sp: argparse.ArgumentParser,
                        kw_opts: Optional[List[str]] = None,
                        pos_opts: Optional[List[str]] = None) -> argparse.ArgumentParser:
    if kw_opts is None:
        kw_opts = []
    if pos_opts is None:
        pos_opts = []

    for opt in kw_opts:
        *pos_args, kw_args = ALEMBIC_KV_OPTS[opt]
        sp.add_argument(*pos_args, **kw_args)

    for opt in pos_opts:
        opt_help = ALEMBIC_POS_OPTS[opt]
        sp.add_argument(opt, help=opt_help)

    return sp
