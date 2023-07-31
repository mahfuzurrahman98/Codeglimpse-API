def tags_arr_to_str(tags_arr):
    for i in range(len(tags_arr)):
        tags_arr[i] = tags_arr[i].strip()
    tags_str = ','.join(tags_arr)
    return tags_str
