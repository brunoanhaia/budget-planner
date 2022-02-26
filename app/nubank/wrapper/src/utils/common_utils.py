def planify_array(array: list[str]):
    result = []
    for elem in array:
        if type(elem) is list:
            planify_array(elem)
        if type(elem) is str:
            result.append(elem)
        else:
            result.extend(elem)

    return result

def card_bill_add_details_from_card_statement(card_bill: dict, card_statements):

    if 'details' in card_bill:
        for transaction in card_bill['details']:
            transaction = transaction_add_details_from_card_statement(
                transaction, card_statements)

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
