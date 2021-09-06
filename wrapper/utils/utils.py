
def planify_array(array: list):
    result = []
    for elem in array:
        if type(elem) is list:
            planify_array(elem)
        if type(elem) is str:
            result.append(elem)
        else:
            result.extend(elem)

    return result

def planify_summary_section(values: dict):

    # Iterate over each key in the summary dictionary
    for key in values['summary']:
        inner_value = values['summary'][key]
        values[key] = inner_value

    values.pop('summary')