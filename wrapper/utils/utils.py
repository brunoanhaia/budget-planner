
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


def group_tags_and_get_amount_from_card_bill(card_bill):
    transactions_with_tag = [
        transaction for transaction in card_bill['details'] if 'tags' in transaction]

    if len(transactions_with_tag) > 0:
        amount_per_tag = get_amount_per_tag(
            transactions_with_tag)
        card_bill['amount_per_tag'] = amount_per_tag

    return card_bill


def get_amount_per_tag(transactions_list: list[dict]) -> dict:
    amount_per_tag_dict = {}

    for transaction in transactions_list:
        tags = planify_array(transaction['tags'])
        amount = transaction['amount']

        for tag in tags:
            if tag in amount_per_tag_dict:
                amount_per_tag_dict[tag] += amount
            else:
                amount_per_tag_dict[tag] = amount

    return amount_per_tag_dict


def card_bill_add_details_from_card_statement(card_bill: dict):

    if 'details' in card_bill:
        for transaction in card_bill['details']:
            transaction = transaction_add_details_from_card_statement(
                transaction)

    return card_bill


def transaction_add_details_from_card_statement(transaction: dict, card_statements):

    statement = [statement for statement in card_statements if (
        'transaction_id' in transaction and statement['id'] == transaction['transaction_id'])]

    if statement != None and len(statement) > 0:
        detail_filter_list = ['tags', 'charges']

        for detail in detail_filter_list:
            st = statement[0]

            if detail in st:
                transaction[detail] = st[detail]

    return transaction
