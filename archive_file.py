#
# (c) 2025 Yoichi Tanibayashi
#
import datetime
import os
import sys

from pyclickutils import click_common_opts, get_logger, import_click


click = import_click()


@click.command()
@click.argument('src_file', type=click.Path())
@click.option(
    '--stat', '-s', type=str,
    default='done', show_default=True,
    help='status'
)
@click.option(
    '--dstdir', '-d', type=str,
    default='archives', show_default=True,
    help='destination directory'
)
@click_common_opts(click, "0.1.0", use_d=False)
def main(ctx, src_file, stat, dstdir, debug):
    """
    指定されたファイルをアーカイブディレクトリに移動し、リネーム。
    """
    log = get_logger(__name__, debug)
    log.debug("click = %a", click.__name__)
    log.debug("command name = %a", ctx.command.name)
    log.debug("stat = %a, dstdir = %s/", stat, dstdir)

    print(f"file: {src_file}")

    # ファイルの存在確認
    if not os.path.exists(src_file):
        log.error("file not found: %a", src_file)
        sys.exit(1)

    # dstdirnoの存在確認
    if not os.path.exists(dstdir):
        log.error("directory not found: %s/", dstdir)
        sys.exit(2)

    # ファイル名と拡張子を分割
    base_name = os.path.basename(src_file)
    file_root, file_ext = os.path.splitext(base_name)
    log.debug(
        "base_name:%a, file_root:%a, file_ext:%a",
        base_name, file_root, file_ext
    )

    # タイムスタンプを付加
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y%m%d-%H%M%S")
    new_filename = f"{timestamp}-{file_root}-{stat}{file_ext}"
    log.debug("new_filename: %a", new_filename)

    # 新しいパスを生成
    new_path = os.path.join(dstdir, new_filename)
    log.debug("new_path: %a", new_path)

    try:
        os.rename(src_file, new_path)
        print(f"Archived '{src_file}' to '{new_path}'")
    except OSError as e:
        log.error("%s: %s", type(e).__name__, e)
        sys.exit(3)

if __name__ == "__main__":
    main()
