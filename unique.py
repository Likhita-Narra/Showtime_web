def unique_multi(list1):
    unique_list = []
    for i in list1:
        for j in i:
            if j not in unique_list:
                unique_list.append(j)
    return unique_list


def unique(list1):
    unique_list = []
    for i in list1:
        if i not in unique_list:
            unique_list.append(i)
    return unique_list



