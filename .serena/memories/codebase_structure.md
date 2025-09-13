src/pi0servo/: Main source directory
    command/: CLI tools (cmd_apiclient, cmd_calib, cmd_servo, cmd_strclient)
    core/: Core servo control logic (piservo, calibrable_servo, multi_servo)
    helper/: Utility functions (str_cmd_to_json, thread_multi_servo, thread_worker)
    utils/: General utilities (click_utils, error_codes, my_logger, servo_config_manager)
    web/: Web API related components (api_client, json_api)