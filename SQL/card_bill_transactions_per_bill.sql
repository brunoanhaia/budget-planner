CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `bruno`@`%` 
    SQL SECURITY DEFINER
VIEW `card_bill_transactions_condensed` AS
    SELECT 
        `card_bill`.`cpf` AS `cpf`,
        `card_bill`.`total_balance` AS `total_balance`,
        `card_bill`.`past_balance` AS `past_balance`,
        `card_bill`.`total_cumulative` AS `total_cumulative`,
        `card_bill`.`state` AS `state`,
        `card_bill`.`close_date` AS `close_date`,
        `card_bill_transaction`.`amount` AS `amount`,
        `card_bill_transaction`.`category` AS `category`,
        `card_bill_transaction`.`post_date` AS `post_date`,
        `card_bill_transaction`.`type` AS `type`,
        `card_bill_transaction`.`index` AS `index`,
        `card_bill_transaction`.`charges` AS `charges`,
        `card_bill_transaction`.`title` AS `title`
    FROM
        (`card_bill`
        LEFT JOIN `card_bill_transaction` ON ((`card_bill`.`id` = `card_bill_transaction`.`card_bill_id`)))