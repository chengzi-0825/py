def fuzzy_replace(original_content: str, old_text: str, new_text: str) -> str:
    """四级降级匹配：精确 -> 换行符归一化 -> 去首尾空白 -> 逐行去缩进"""
    # L1 精确匹配
    count = original_content.count(old_text)
    if count == 1:
        return original_content.replace(old_text, new_text)
    if count > 1:
        raise RuntimeError(f"匹配到了 {count} 处，请提供更多上下文")

    # L2 换行符归一化
    norm_ori = original_content.replace("\r\n", "\n")
    norm_old = old_text.replace("\r\n", "\n")
    cnt2 = norm_ori.count(norm_old)
    if cnt2 == 1:
        return norm_ori.replace(norm_old, new_text)
    if cnt2 > 1:
        raise RuntimeError(f"换行归一化后匹配到 {cnt2} 处，请提供更多上下文")

    # L3 整体去首尾空白
    strip_old = norm_old.strip()
    if strip_old:
        cnt3 = norm_ori.count(strip_old)
        if cnt3 == 1:
            return norm_ori.replace(strip_old, new_text)
        if cnt3 > 1:
            raise RuntimeError(f"去空白后匹配到 {cnt3} 处，请提供更多上下文")

    # L4 逐行去缩进降级
    return line_by_line_replace(norm_ori, norm_old, new_text)


def line_by_line_replace(content: str, old_text: str, new_text: str) -> str:
    content_lines = content.splitlines(keepends=True)
    old_lines = old_text.splitlines()
    match_count = 0
    match_positions = []
    n_old = len(old_lines)

    for i in range(len(content_lines) - n_old + 1):
        window = content_lines[i:i+n_old]
        match = True
        for cl, ol in zip(window, old_lines):
            if cl.lstrip() != ol.lstrip():
                match = False
                break
        if match:
            match_count +=1
            match_positions.append(i)

    # 唯一性安全底线
    if match_count == 0:
        raise RuntimeError("在文件中未找到 old_text，请检查内容和缩进")
    if match_count > 1:
        raise RuntimeError(f"模糊匹配到了 {match_count} 处代码，请提供更多上下文以定位")

    # 执行替换
    start = match_positions[0]
    new_lines = content_lines[:start] + [new_text] + content_lines[start + n_old:]
    return "".join(new_lines)