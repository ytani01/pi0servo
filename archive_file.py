#
# (c) 2025 Yoichi Tanibayashi
#
import os
import datetime

from clickutils import click, click_common_opts, get_logger

@click.command()
@click.argument('target_file', type=click.Path())
@click.option('--archive-path', default='archives', help='アーカイブ先のディレクトリ')
@click_common_opts()
def main(ctx, archive_path, target_file, debug):
    """
    指定されたファイルをアーカイブディレクトリに移動し、リネームします。
    """
    log = get_logger(__name__, debug)
    log.debug("command name = %a", ctx.command.name)
    log.debug("archive_path = %s", archive_path)

    print(f"Target file: {target_file}")

    if not os.path.exists(target_file):
        log.error(f"Error: File not found: {target_file}")
        ctx.exit(1) # エラー終了

    # archives ディレクトリが存在しない場合は作成
    archive_dir_to_use = archive_path
    if not os.path.exists(archive_dir_to_use):
        os.makedirs(archive_dir_to_use)
        log.debug("Created directory: %s", archive_dir_to_use)

    # ファイル名と拡張子を分割
    base_name = os.path.basename(target_file)
    file_root, file_ext = os.path.splitext(base_name)

    # タイムスタンプを付加
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("-%Y%m%d-%H%M%S")
    new_filename = f"{file_root}{timestamp}{file_ext}"

    # 新しいパスを生成
    new_path = os.path.join(archive_path, new_filename)

    try:
        os.rename(target_file, new_path)
        print(f"Archived '{target_file}' to '{new_path}'")
    except OSError as e:
        log.error(f"Error archiving file: {e}")
        ctx.exit(1) # エラー終了

if __name__ == "__main__":
    main()
