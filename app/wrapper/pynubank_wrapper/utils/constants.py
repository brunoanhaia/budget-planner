class Constants():
    
    class Keyring():
        secret = 'KEYRING-SECRET'
        user_mask = 'KEYRING-MASK'
        user_token_mask = 'KEYRING-TKMASK'

    class Log():
        level = 'LOG_LEVEL'
    
    class Wrapper():
        standalone_run = 'STANDALONE_RUN'
        use_localappdata = 'USE_LOCAL_APP_DATA' 
        cache_dir_name = 'CACHE_DIR_NAME'
        cache_dir_path = 'CACHE_DIR_PATH'
        user_cache_dir_name = 'USER_CACHE_DIR_NAME'
        user_cache_dir_path = 'USER_CACHE_DIR_PATH'
        user_certificate_mask = 'CERTIFICATE_MASK'
        user_certificate_path = 'CERTIFICATE_PATH'

        class Path():
            account_feed = 'account_feed'
            account_statement_file = 'account_statement'
            account_monthly_summary_file = 'account_statement_summary'
            card_feed_file = 'card_feed'
            card_statements_file = 'card_statements'
            card_bill_folder = 'card_bill'
            card_bill_transactions_folder = 'card_bill_transactions'
            card_bill_amount_per_tag_file = 'card_bill_amount_per_tag'
            card_bill_amount_per_category_file = 'card_bill_amount_per_category'
            certificate_suffix = '_cert.p12'
            token_suffix = '.token'
