import os
import argparse
import sys
from jinja2 import Template


def generate_tree(
    root_path, show_hidden=False, max_depth=None, current_depth=0, prefix="", is_last=False, is_root=True
):
    """生成目录树结构的核心函数"""
    lines = []
    dir_count = 0
    file_count = 0

    # 处理根目录显示
    if is_root:
        name = os.path.basename(root_path)
        display_name = f"{name}{os.sep}" if os.path.isdir(root_path) else name
        lines.append(display_name)
        if not os.path.isdir(root_path):
            return lines, 0, 1  # 如果是文件直接返回

    # 达到最大深度时停止递归
    if max_depth is not None and current_depth >= max_depth:
        return lines, dir_count, file_count

    # 获取目录内容（处理权限问题）
    try:
        entries = os.listdir(root_path)
    except PermissionError:
        lines.append(f"{prefix}└── [Permission denied]")
        return lines, dir_count, file_count

    # 过滤隐藏文件
    if not show_hidden:
        entries = [e for e in entries if not e.startswith(".")]

    # 排序处理：目录在前，文件在后，均按字母排序
    entries.sort(key=lambda x: x.lower())
    dirs = [e for e in entries if os.path.isdir(os.path.join(root_path, e))]
    files = [e for e in entries if not os.path.isdir(os.path.join(root_path, e))]
    sorted_entries = dirs + files

    for index, entry in enumerate(sorted_entries):
        is_last_entry = index == len(sorted_entries) - 1
        entry_path = os.path.join(root_path, entry)
        is_directory = os.path.isdir(entry_path)

        # 生成当前条目显示
        connector = "└── " if is_last_entry else "├── "
        lines.append(f"{prefix}{connector}{entry}")

        # 递归处理子目录
        if is_directory:
            dir_count += 1
            extension = "    " if is_last_entry else "│   "
            sub_lines, sub_dirs, sub_files = generate_tree(
                entry_path,
                show_hidden=show_hidden,
                max_depth=max_depth,
                current_depth=current_depth + 1,
                prefix=prefix + extension,
                is_last=is_last_entry,
                is_root=False,
            )
            lines.extend(sub_lines)
            dir_count += sub_dirs
            file_count += sub_files
        else:
            file_count += 1

    return lines, dir_count, file_count


def main():
    """主函数处理参数解析和输出"""
    parser = argparse.ArgumentParser(description="生成目录树结构")
    parser.add_argument("directory", nargs="?", default=os.getcwd(), help="目标目录（默认为当前目录）")
    parser.add_argument("-a", "--all", action="store_true", help="显示隐藏文件")
    parser.add_argument("-d", "--max-depth", type=int, help="设置遍历深度限制")
    parser.add_argument("-o", "--output", help="输出到指定文件")
    parser.add_argument("-t", "--template", help="根据模板输出到指定文件")

    args = parser.parse_args()

    # 验证路径有效性
    if not os.path.exists(args.directory):
        print(f"错误：路径 '{args.directory}' 不存在")
        sys.exit(1)

    # 生成目录树
    tree_lines, dir_count, file_count = generate_tree(
        args.directory, show_hidden=args.all, max_depth=args.max_depth
    )

    output = "\n".join(tree_lines)

    # 处理输出方式
    if args.output:
        if args.template:
            with open(args.template, "r", encoding="utf-8") as f:
                template = Template(f.read())
            output = template.render(content=output)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        output = "\n".join(tree_lines)
        print(output)


if __name__ == "__main__":
    main()
