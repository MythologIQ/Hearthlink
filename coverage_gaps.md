# Coverage Gaps Analysis

**Generated:** 2025-08-01T00:11:21.735228
**Project:** /mnt/g/mythologiq/hearthlink

## Executive Summary

- **Total Functions/Endpoints:** 3856
- **Coverage Gaps:** 1752
- **Current Coverage:** 54.6%
- **Target Coverage:** ≥95%

### Gap Breakdown

- **Test Coverage Gaps:** 1223
- **UI Invocation Gaps:** 1752
- **CLI Invocation Gaps:** 1315

### Priority Breakdown

- **Critical:** 1177
- **High:** 494
- **Medium:** 81
- **Low:** 0

## Critical Gaps (Immediate Action Required)

### create_agent
**File:** `src/api_server.py:88`
**Module:** `src.api_server`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for create_agent if user-facing
- Consider adding CLI command for create_agent if appropriate

### create_token
**File:** `src/api_server.py:199`
**Module:** `src.api_server`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_token
- Consider adding UI control for create_token if user-facing
- Consider adding CLI command for create_token if appropriate

### execute_command
**File:** `src/api_server.py:338`
**Module:** `src.api_server`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_command
- Consider adding UI control for execute_command if user-facing
- Add CLI command wrapper for execute_command

### get_status
**File:** `src/main.py:606`
**Module:** `src.main`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### get_llm_config
**File:** `src/run_alden.py:57`
**Module:** `src.run_alden`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_llm_config
- Consider adding UI control for get_llm_config if user-facing
- Consider adding CLI command for get_llm_config if appropriate

### run_cli
**File:** `src/run_alden.py:85`
**Module:** `src.run_alden`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for run_cli
- Consider adding UI control for run_cli if user-facing
- Consider adding CLI command for run_cli if appropriate

### run_api
**File:** `src/run_alden.py:97`
**Module:** `src.run_alden`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for run_api
- Add UI button/form calling run_api in appropriate React component
- Consider adding CLI command for run_api if appropriate

### create_alden_api
**File:** `src/api/alden_api.py:401`
**Module:** `src.api.alden_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_alden_api
- Add UI button/form calling create_alden_api in appropriate React component
- Consider adding CLI command for create_alden_api if appropriate

### update_trait
**File:** `src/api/alden_api.py:201`
**Module:** `src.api.alden_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_trait
- Consider adding UI control for update_trait if user-facing
- Consider adding CLI command for update_trait if appropriate

### get_status
**File:** `src/api/alden_api.py:289`
**Module:** `src.api.alden_api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### get_version
**File:** `src/api/claude_code_cli.py:60`
**Module:** `src.api.claude_code_cli`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_version
- Consider adding UI control for get_version if user-facing
- Consider adding CLI command for get_version if appropriate

### execute_command
**File:** `src/api/claude_code_cli.py:89`
**Module:** `src.api.claude_code_cli`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_command
- Consider adding UI control for execute_command if user-facing
- Add CLI command wrapper for execute_command

### get_session_history
**File:** `src/api/claude_code_cli.py:234`
**Module:** `src.api.claude_code_cli`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_session_history
- Consider adding UI control for get_session_history if user-facing
- Consider adding CLI command for get_session_history if appropriate

### get_current_session
**File:** `src/api/claude_code_cli.py:238`
**Module:** `src.api.claude_code_cli`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_current_session
- Consider adding UI control for get_current_session if user-facing
- Consider adding CLI command for get_current_session if appropriate

### get_available_commands
**File:** `src/api/claude_code_cli.py:265`
**Module:** `src.api.claude_code_cli`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_available_commands
- Consider adding UI control for get_available_commands if user-facing
- Consider adding CLI command for get_available_commands if appropriate

### get_status
**File:** `src/api/claude_code_cli.py:304`
**Module:** `src.api.claude_code_cli`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### update_agent_statuses
**File:** `src/api/core_api.py:44`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_agent_statuses
- Consider adding UI control for update_agent_statuses if user-facing
- Consider adding CLI command for update_agent_statuses if appropriate

### update_service_statuses
**File:** `src/api/core_api.py:74`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_service_statuses
- Consider adding UI control for update_service_statuses if user-facing
- Consider adding CLI command for update_service_statuses if appropriate

### get_agents
**File:** `src/api/core_api.py:287`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agents
- Consider adding UI control for get_agents if user-facing
- Consider adding CLI command for get_agents if appropriate

### update_agent
**File:** `src/api/core_api.py:309`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_agent
- Consider adding UI control for update_agent if user-facing
- Consider adding CLI command for update_agent if appropriate

### get_services
**File:** `src/api/core_api.py:323`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_services
- Consider adding UI control for get_services if user-facing
- Consider adding CLI command for get_services if appropriate

### get_projects
**File:** `src/api/core_api.py:354`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_projects
- Consider adding UI control for get_projects if user-facing
- Consider adding CLI command for get_projects if appropriate

### create_project
**File:** `src/api/core_api.py:362`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_project
- Consider adding UI control for create_project if user-facing
- Consider adding CLI command for create_project if appropriate

### get_project
**File:** `src/api/core_api.py:391`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_project
- Consider adding UI control for get_project if user-facing
- Consider adding CLI command for get_project if appropriate

### get_sessions
**File:** `src/api/core_api.py:445`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_sessions
- Consider adding UI control for get_sessions if user-facing
- Consider adding CLI command for get_sessions if appropriate

### get_orchestration_status
**File:** `src/api/core_api.py:533`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_orchestration_status
- Consider adding UI control for get_orchestration_status if user-facing
- Consider adding CLI command for get_orchestration_status if appropriate

### get_orchestration_logs
**File:** `src/api/core_api.py:549`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_orchestration_logs
- Consider adding UI control for get_orchestration_logs if user-facing
- Consider adding CLI command for get_orchestration_logs if appropriate

### get_system_metrics
**File:** `src/api/core_api.py:558`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_system_metrics if user-facing
- Consider adding CLI command for get_system_metrics if appropriate

### get_system_memory
**File:** `src/api/core_api.py:570`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_system_memory
- Consider adding UI control for get_system_memory if user-facing
- Consider adding CLI command for get_system_memory if appropriate

### get_system_health
**File:** `src/api/core_api.py:622`
**Module:** `src.api.core_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_system_health
- Consider adding UI control for get_system_health if user-facing
- Consider adding CLI command for get_system_health if appropriate

### get_enhanced_core
**File:** `src/api/enhanced_core_api.py:70`
**Module:** `src.api.enhanced_core_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_enhanced_core
- Consider adding UI control for get_enhanced_core if user-facing
- Consider adding CLI command for get_enhanced_core if appropriate

### create_agentic_session
**File:** `src/api/enhanced_core_api.py:86`
**Module:** `src.api.enhanced_core_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_agentic_session
- Consider adding UI control for create_agentic_session if user-facing
- Consider adding CLI command for create_agentic_session if appropriate

### execute_agentic_task
**File:** `src/api/enhanced_core_api.py:111`
**Module:** `src.api.enhanced_core_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_agentic_task
- Consider adding UI control for execute_agentic_task if user-facing
- Add CLI command wrapper for execute_agentic_task

### get_agent_capabilities
**File:** `src/api/enhanced_core_api.py:176`
**Module:** `src.api.enhanced_core_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_capabilities
- Consider adding UI control for get_agent_capabilities if user-facing
- Consider adding CLI command for get_agent_capabilities if appropriate

### get_workflow_status
**File:** `src/api/enhanced_core_api.py:191`
**Module:** `src.api.enhanced_core_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_workflow_status
- Consider adding UI control for get_workflow_status if user-facing
- Consider adding CLI command for get_workflow_status if appropriate

### get_enhanced_session_info
**File:** `src/api/enhanced_core_api.py:244`
**Module:** `src.api.enhanced_core_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_enhanced_session_info
- Consider adding UI control for get_enhanced_session_info if user-facing
- Consider adding CLI command for get_enhanced_session_info if appropriate

### get_session_workflows
**File:** `src/api/enhanced_core_api.py:264`
**Module:** `src.api.enhanced_core_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_session_workflows
- Consider adding UI control for get_session_workflows if user-facing
- Consider adding CLI command for get_session_workflows if appropriate

### get_agent_delegations
**File:** `src/api/enhanced_core_api.py:300`
**Module:** `src.api.enhanced_core_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_delegations
- Consider adding UI control for get_agent_delegations if user-facing
- Consider adding CLI command for get_agent_delegations if appropriate

### get_agent_status
**File:** `src/api/external_agent_api.py:197`
**Module:** `src.api.external_agent_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_status
- Consider adding UI control for get_agent_status if user-facing
- Consider adding CLI command for get_agent_status if appropriate

### execute_agent_action
**File:** `src/api/external_agent_api.py:226`
**Module:** `src.api.external_agent_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_agent_action
- Consider adding UI control for execute_agent_action if user-facing
- Add CLI command wrapper for execute_agent_action

### get_circuit_breakers_status
**File:** `src/api/external_agent_api.py:437`
**Module:** `src.api.external_agent_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_circuit_breakers_status
- Consider adding UI control for get_circuit_breakers_status if user-facing
- Consider adding CLI command for get_circuit_breakers_status if appropriate

### get_agent_instance
**File:** `src/api/external_agent_api.py:88`
**Module:** `src.api.external_agent_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_instance
- Consider adding UI control for get_agent_instance if user-facing
- Consider adding CLI command for get_agent_instance if appropriate

### execute_agent_request
**File:** `src/api/external_agent_api.py:129`
**Module:** `src.api.external_agent_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_agent_request
- Consider adding UI control for execute_agent_request if user-facing
- Add CLI command wrapper for execute_agent_request

### get_kimi_k2_backend
**File:** `src/api/kimi_k2_api.py:76`
**Module:** `src.api.kimi_k2_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_kimi_k2_backend
- Consider adding UI control for get_kimi_k2_backend if user-facing
- Consider adding CLI command for get_kimi_k2_backend if appropriate

### get_stats
**File:** `src/api/kimi_k2_api.py:314`
**Module:** `src.api.kimi_k2_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_stats
- Consider adding UI control for get_stats if user-facing
- Consider adding CLI command for get_stats if appropriate

### get_capabilities
**File:** `src/api/kimi_k2_api.py:338`
**Module:** `src.api.kimi_k2_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_capabilities
- Consider adding UI control for get_capabilities if user-facing
- Consider adding CLI command for get_capabilities if appropriate

### get_metrics
**File:** `src/api/kimi_k2_api.py:401`
**Module:** `src.api.kimi_k2_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_metrics
- Consider adding UI control for get_metrics if user-facing
- Consider adding CLI command for get_metrics if appropriate

### get_current_user
**File:** `src/api/license_validation.py:76`
**Module:** `src.api.license_validation`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_current_user
- Consider adding UI control for get_current_user if user-facing
- Consider adding CLI command for get_current_user if appropriate

### get_license_usage
**File:** `src/api/license_validation.py:98`
**Module:** `src.api.license_validation`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_license_usage
- Consider adding UI control for get_license_usage if user-facing
- Consider adding CLI command for get_license_usage if appropriate

### update_license_usage
**File:** `src/api/license_validation.py:121`
**Module:** `src.api.license_validation`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_license_usage
- Consider adding UI control for update_license_usage if user-facing
- Consider adding CLI command for update_license_usage if appropriate

### get_template_license_info
**File:** `src/api/license_validation.py:326`
**Module:** `src.api.license_validation`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_template_license_info
- Consider adding UI control for get_template_license_info if user-facing
- Consider adding CLI command for get_template_license_info if appropriate

### get_user_licenses
**File:** `src/api/license_validation.py:353`
**Module:** `src.api.license_validation`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_user_licenses
- Consider adding UI control for get_user_licenses if user-facing
- Consider adding CLI command for get_user_licenses if appropriate

### get_model_info
**File:** `src/api/llm_connector.py:45`
**Module:** `src.api.llm_connector`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_model_info
- Consider adding UI control for get_model_info if user-facing
- Consider adding CLI command for get_model_info if appropriate

### get_status
**File:** `src/api/llm_connector.py:77`
**Module:** `src.api.llm_connector`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### update_metrics
**File:** `src/api/local_llm_api.py:217`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_metrics
- Consider adding UI control for update_metrics if user-facing
- Consider adding CLI command for update_metrics if appropriate

### get_status
**File:** `src/api/local_llm_api.py:273`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### get_models
**File:** `src/api/local_llm_api.py:279`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_models
- Consider adding UI control for get_models if user-facing
- Consider adding CLI command for get_models if appropriate

### get_profiles
**File:** `src/api/local_llm_api.py:436`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_profiles
- Consider adding UI control for get_profiles if user-facing
- Consider adding CLI command for get_profiles if appropriate

### update_profiles
**File:** `src/api/local_llm_api.py:441`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_profiles
- Consider adding UI control for update_profiles if user-facing
- Consider adding CLI command for update_profiles if appropriate

### get_metrics
**File:** `src/api/local_llm_api.py:520`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_metrics
- Consider adding UI control for get_metrics if user-facing
- Consider adding CLI command for get_metrics if appropriate

### get_model_recommendations
**File:** `src/api/local_llm_api.py:535`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_model_recommendations
- Consider adding UI control for get_model_recommendations if user-facing
- Consider adding CLI command for get_model_recommendations if appropriate

### get_connection_pool_status
**File:** `src/api/local_llm_api.py:699`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_connection_pool_status
- Consider adding UI control for get_connection_pool_status if user-facing
- Consider adding CLI command for get_connection_pool_status if appropriate

### get_system_specs
**File:** `src/api/local_llm_api.py:743`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_system_specs
- Consider adding UI control for get_system_specs if user-facing
- Consider adding CLI command for get_system_specs if appropriate

### get_offline_status
**File:** `src/api/local_llm_api.py:822`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_offline_status
- Consider adding UI control for get_offline_status if user-facing
- Consider adding CLI command for get_offline_status if appropriate

### get_cached_models
**File:** `src/api/local_llm_api.py:915`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_cached_models
- Consider adding UI control for get_cached_models if user-facing
- Consider adding CLI command for get_cached_models if appropriate

### get_circuit_breaker_status
**File:** `src/api/local_llm_api.py:994`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_circuit_breaker_status
- Consider adding UI control for get_circuit_breaker_status if user-facing
- Consider adding CLI command for get_circuit_breaker_status if appropriate

### get_settings
**File:** `src/api/local_llm_api.py:1093`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_settings
- Consider adding UI control for get_settings if user-facing
- Consider adding CLI command for get_settings if appropriate

### get_claude_code_status
**File:** `src/api/local_llm_api.py:1129`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_claude_code_status
- Consider adding UI control for get_claude_code_status if user-facing
- Consider adding CLI command for get_claude_code_status if appropriate

### get_available_endpoint
**File:** `src/api/local_llm_api.py:96`
**Module:** `src.api.local_llm_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_available_endpoint
- Consider adding UI control for get_available_endpoint if user-facing
- Consider adding CLI command for get_available_endpoint if appropriate

### get_current_user
**File:** `src/api/metrics.py:69`
**Module:** `src.api.metrics`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_current_user
- Consider adding UI control for get_current_user if user-facing
- Consider adding CLI command for get_current_user if appropriate

### update_system_health
**File:** `src/api/metrics.py:150`
**Module:** `src.api.metrics`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_system_health
- Consider adding UI control for update_system_health if user-facing
- Consider adding CLI command for update_system_health if appropriate

### get_system_health
**File:** `src/api/metrics.py:221`
**Module:** `src.api.metrics`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_system_health
- Consider adding UI control for get_system_health if user-facing
- Consider adding CLI command for get_system_health if appropriate

### get_spec2_compliance
**File:** `src/api/metrics.py:233`
**Module:** `src.api.metrics`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_spec2_compliance
- Consider adding UI control for get_spec2_compliance if user-facing
- Consider adding CLI command for get_spec2_compliance if appropriate

### run_smoke_tests
**File:** `src/api/metrics.py:268`
**Module:** `src.api.metrics`
**Type:** async_function
**Missing:** test, ui_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for run_smoke_tests
- Consider adding UI control for run_smoke_tests if user-facing

### run_load_tests
**File:** `src/api/metrics.py:303`
**Module:** `src.api.metrics`
**Type:** async_function
**Missing:** test, ui_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for run_load_tests
- Consider adding UI control for run_load_tests if user-facing

### get_real_time_metrics
**File:** `src/api/metrics.py:339`
**Module:** `src.api.metrics`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_real_time_metrics
- Consider adding UI control for get_real_time_metrics if user-facing
- Consider adding CLI command for get_real_time_metrics if appropriate

### get_dashboard_summary
**File:** `src/api/metrics.py:365`
**Module:** `src.api.metrics`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_dashboard_summary
- Consider adding UI control for get_dashboard_summary if user-facing
- Consider adding CLI command for get_dashboard_summary if appropriate

### get_current_user
**File:** `src/api/mimic_api.py:182`
**Module:** `src.api.mimic_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_current_user
- Consider adding UI control for get_current_user if user-facing
- Consider adding CLI command for get_current_user if appropriate

### get_mimic_persona
**File:** `src/api/mimic_api.py:193`
**Module:** `src.api.mimic_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_mimic_persona
- Consider adding UI control for get_mimic_persona if user-facing
- Consider adding CLI command for get_mimic_persona if appropriate

### get_performance_analytics
**File:** `src/api/mimic_api.py:291`
**Module:** `src.api.mimic_api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_performance_analytics if user-facing
- Consider adding CLI command for get_performance_analytics if appropriate

### get_plugin_extensions
**File:** `src/api/mimic_api.py:450`
**Module:** `src.api.mimic_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_plugin_extensions
- Consider adding UI control for get_plugin_extensions if user-facing
- Consider adding CLI command for get_plugin_extensions if appropriate

### get_knowledge
**File:** `src/api/mimic_api.py:515`
**Module:** `src.api.mimic_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_knowledge
- Consider adding UI control for get_knowledge if user-facing
- Consider adding CLI command for get_knowledge if appropriate

### get_persona_status
**File:** `src/api/mimic_api.py:540`
**Module:** `src.api.mimic_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_persona_status
- Consider adding UI control for get_persona_status if user-facing
- Consider adding CLI command for get_persona_status if appropriate

### get_performance_tier
**File:** `src/api/mimic_api.py:565`
**Module:** `src.api.mimic_api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_performance_tier if user-facing
- Consider adding CLI command for get_performance_tier if appropriate

### delete_persona
**File:** `src/api/mimic_api.py:671`
**Module:** `src.api.mimic_api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for delete_persona
- Consider adding UI control for delete_persona if user-facing
- Consider adding CLI command for delete_persona if appropriate

### get_system_status
**File:** `src/api/offline_llm_manager.py:514`
**Module:** `src.api.offline_llm_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_system_status if user-facing
- Consider adding CLI command for get_system_status if appropriate

### get_vault_metrics
**File:** `src/api/sentry_api.py:111`
**Module:** `src.api.sentry_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_vault_metrics
- Consider adding UI control for get_vault_metrics if user-facing
- Consider adding CLI command for get_vault_metrics if appropriate

### get_claude_connector_metrics
**File:** `src/api/sentry_api.py:165`
**Module:** `src.api.sentry_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_claude_connector_metrics
- Consider adding UI control for get_claude_connector_metrics if user-facing
- Consider adding CLI command for get_claude_connector_metrics if appropriate

### get_synapse_gateway_metrics
**File:** `src/api/sentry_api.py:198`
**Module:** `src.api.sentry_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_synapse_gateway_metrics
- Consider adding UI control for get_synapse_gateway_metrics if user-facing
- Consider adding CLI command for get_synapse_gateway_metrics if appropriate

### get_launch_page_metrics
**File:** `src/api/sentry_api.py:241`
**Module:** `src.api.sentry_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_launch_page_metrics
- Consider adding UI control for get_launch_page_metrics if user-facing
- Consider adding CLI command for get_launch_page_metrics if appropriate

### get_token_usage_metrics
**File:** `src/api/sentry_api.py:272`
**Module:** `src.api.sentry_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_token_usage_metrics
- Consider adding UI control for get_token_usage_metrics if user-facing
- Consider adding CLI command for get_token_usage_metrics if appropriate

### get_system_metrics
**File:** `src/api/sentry_api.py:300`
**Module:** `src.api.sentry_api`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_system_metrics if user-facing
- Consider adding CLI command for get_system_metrics if appropriate

### update_system_health
**File:** `src/api/sentry_api.py:317`
**Module:** `src.api.sentry_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_system_health
- Consider adding UI control for update_system_health if user-facing
- Consider adding CLI command for update_system_health if appropriate

### get_system_health
**File:** `src/api/sentry_api.py:413`
**Module:** `src.api.sentry_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_system_health
- Consider adding UI control for get_system_health if user-facing
- Consider adding CLI command for get_system_health if appropriate

### get_recent_events
**File:** `src/api/sentry_api.py:418`
**Module:** `src.api.sentry_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_recent_events
- Consider adding UI control for get_recent_events if user-facing
- Consider adding CLI command for get_recent_events if appropriate

### get_active_alerts
**File:** `src/api/sentry_api.py:427`
**Module:** `src.api.sentry_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_active_alerts
- Consider adding UI control for get_active_alerts if user-facing
- Consider adding CLI command for get_active_alerts if appropriate

### start_monitoring_endpoint
**File:** `src/api/sentry_api.py:461`
**Module:** `src.api.sentry_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_monitoring_endpoint
- Consider adding UI control for start_monitoring_endpoint if user-facing
- Consider adding CLI command for start_monitoring_endpoint if appropriate

### stop_monitoring_endpoint
**File:** `src/api/sentry_api.py:467`
**Module:** `src.api.sentry_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for stop_monitoring_endpoint
- Consider adding UI control for stop_monitoring_endpoint if user-facing
- Consider adding CLI command for stop_monitoring_endpoint if appropriate

### get_monitoring_status
**File:** `src/api/sentry_api.py:473`
**Module:** `src.api.sentry_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_monitoring_status
- Consider adding UI control for get_monitoring_status if user-facing
- Consider adding CLI command for get_monitoring_status if appropriate

### get_settings
**File:** `src/api/settings_api.py:136`
**Module:** `src.api.settings_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_settings
- Consider adding UI control for get_settings if user-facing
- Consider adding CLI command for get_settings if appropriate

### update_settings
**File:** `src/api/settings_api.py:142`
**Module:** `src.api.settings_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_settings
- Consider adding UI control for update_settings if user-facing
- Consider adding CLI command for update_settings if appropriate

### get_ollama_models
**File:** `src/api/settings_api.py:340`
**Module:** `src.api.settings_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_ollama_models
- Consider adding UI control for get_ollama_models if user-facing
- Consider adding CLI command for get_ollama_models if appropriate

### get_services
**File:** `src/api/simple_backend.py:53`
**Module:** `src.api.simple_backend`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_services
- Consider adding UI control for get_services if user-facing
- Consider adding CLI command for get_services if appropriate

### get_stats
**File:** `src/api/simple_backend.py:102`
**Module:** `src.api.simple_backend`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_stats
- Consider adding UI control for get_stats if user-facing
- Consider adding CLI command for get_stats if appropriate

### get_settings
**File:** `src/api/simple_backend.py:144`
**Module:** `src.api.simple_backend`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_settings
- Consider adding UI control for get_settings if user-facing
- Consider adding CLI command for get_settings if appropriate

### get_status
**File:** `src/api/simple_backend.py:182`
**Module:** `src.api.simple_backend`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### get_status
**File:** `src/api/superclaude_api.py:265`
**Module:** `src.api.superclaude_api`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### delete_session
**File:** `src/api/superclaude_api.py:440`
**Module:** `src.api.superclaude_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for delete_session
- Consider adding UI control for delete_session if user-facing
- Consider adding CLI command for delete_session if appropriate

### get_circuit_breakers_status
**File:** `src/api/superclaude_api.py:466`
**Module:** `src.api.superclaude_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_circuit_breakers_status
- Consider adding UI control for get_circuit_breakers_status if user-facing
- Consider adding CLI command for get_circuit_breakers_status if appropriate

### get_context
**File:** `src/api/superclaude_api.py:105`
**Module:** `src.api.superclaude_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_context
- Consider adding UI control for get_context if user-facing
- Consider adding CLI command for get_context if appropriate

### update_token_usage
**File:** `src/api/superclaude_api.py:114`
**Module:** `src.api.superclaude_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_token_usage
- Consider adding UI control for update_token_usage if user-facing
- Consider adding CLI command for update_token_usage if appropriate

### execute_command
**File:** `src/api/superclaude_api.py:162`
**Module:** `src.api.superclaude_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_command
- Consider adding UI control for execute_command if user-facing
- Add CLI command wrapper for execute_command

### execute_request
**File:** `src/api/superclaude_api.py:233`
**Module:** `src.api.superclaude_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_request
- Consider adding UI control for execute_request if user-facing
- Add CLI command wrapper for execute_request

### call_claude_api
**File:** `src/api/synapse_connector.py:101`
**Module:** `src.api.synapse_connector`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for call_claude_api
- Add UI button/form calling call_claude_api in appropriate React component
- Consider adding CLI command for call_claude_api if appropriate

### call_google_ai_api
**File:** `src/api/synapse_connector.py:132`
**Module:** `src.api.synapse_connector`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for call_google_ai_api
- Add UI button/form calling call_google_ai_api in appropriate React component
- Consider adding CLI command for call_google_ai_api if appropriate

### get_connection_status
**File:** `src/api/synapse_connector.py:161`
**Module:** `src.api.synapse_connector`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_connection_status
- Consider adding UI control for get_connection_status if user-facing
- Consider adding CLI command for get_connection_status if appropriate

### get_available_models
**File:** `src/api/synapse_connector.py:173`
**Module:** `src.api.synapse_connector`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_available_models
- Consider adding UI control for get_available_models if user-facing
- Consider adding CLI command for get_available_models if appropriate

### get_memory_usage
**File:** `src/api/system_health.py:192`
**Module:** `src.api.system_health`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_memory_usage
- Consider adding UI control for get_memory_usage if user-facing
- Consider adding CLI command for get_memory_usage if appropriate

### get_current_user
**File:** `src/api/task_templates.py:117`
**Module:** `src.api.task_templates`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_current_user
- Consider adding UI control for get_current_user if user-facing
- Consider adding CLI command for get_current_user if appropriate

### get_templates
**File:** `src/api/task_templates.py:211`
**Module:** `src.api.task_templates`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_templates
- Consider adding UI control for get_templates if user-facing
- Consider adding CLI command for get_templates if appropriate

### get_template
**File:** `src/api/task_templates.py:248`
**Module:** `src.api.task_templates`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_template
- Consider adding UI control for get_template if user-facing
- Consider adding CLI command for get_template if appropriate

### create_template
**File:** `src/api/task_templates.py:279`
**Module:** `src.api.task_templates`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_template
- Consider adding UI control for create_template if user-facing
- Consider adding CLI command for create_template if appropriate

### update_template
**File:** `src/api/task_templates.py:319`
**Module:** `src.api.task_templates`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_template
- Consider adding UI control for update_template if user-facing
- Consider adding CLI command for update_template if appropriate

### delete_template
**File:** `src/api/task_templates.py:366`
**Module:** `src.api.task_templates`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for delete_template
- Consider adding UI control for delete_template if user-facing
- Consider adding CLI command for delete_template if appropriate

### get_audit_trail
**File:** `src/api/task_templates.py:423`
**Module:** `src.api.task_templates`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_audit_trail
- Consider adding UI control for get_audit_trail if user-facing
- Consider adding CLI command for get_audit_trail if appropriate

### get_vault_stats
**File:** `src/api/vault_api.py:83`
**Module:** `src.api.vault_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_vault_stats
- Consider adding UI control for get_vault_stats if user-facing
- Consider adding CLI command for get_vault_stats if appropriate

### get_memories
**File:** `src/api/vault_api.py:111`
**Module:** `src.api.vault_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_memories
- Consider adding UI control for get_memories if user-facing
- Consider adding CLI command for get_memories if appropriate

### create_memory
**File:** `src/api/vault_api.py:155`
**Module:** `src.api.vault_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_memory
- Consider adding UI control for create_memory if user-facing
- Consider adding CLI command for create_memory if appropriate

### get_memory
**File:** `src/api/vault_api.py:190`
**Module:** `src.api.vault_api`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_memory if user-facing
- Consider adding CLI command for get_memory if appropriate

### update_memory
**File:** `src/api/vault_api.py:209`
**Module:** `src.api.vault_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_memory
- Consider adding UI control for update_memory if user-facing
- Consider adding CLI command for update_memory if appropriate

### delete_memory
**File:** `src/api/vault_api.py:238`
**Module:** `src.api.vault_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for delete_memory
- Consider adding UI control for delete_memory if user-facing
- Consider adding CLI command for delete_memory if appropriate

### get_audit_log
**File:** `src/api/vault_api.py:262`
**Module:** `src.api.vault_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_audit_log
- Consider adding UI control for get_audit_log if user-facing
- Consider adding CLI command for get_audit_log if appropriate

### create_backup
**File:** `src/api/vault_api.py:291`
**Module:** `src.api.vault_api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_backup
- Consider adding UI control for create_backup if user-facing
- Consider adding CLI command for create_backup if appropriate

### get_persona
**File:** `src/api/vault_connector.py:140`
**Module:** `src.api.vault_connector`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_persona if user-facing
- Consider adding CLI command for get_persona if appropriate

### get_memories
**File:** `src/api/vault_connector.py:187`
**Module:** `src.api.vault_connector`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_memories
- Consider adding UI control for get_memories if user-facing
- Consider adding CLI command for get_memories if appropriate

### get_system_logs
**File:** `src/api/vault_connector.py:245`
**Module:** `src.api.vault_connector`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_system_logs
- Consider adding UI control for get_system_logs if user-facing
- Consider adding CLI command for get_system_logs if appropriate

### get_status
**File:** `src/api/vault_connector.py:275`
**Module:** `src.api.vault_connector`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### get_stats
**File:** `src/api/vault_connector.py:313`
**Module:** `src.api.vault_connector`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_stats
- Consider adding UI control for get_stats if user-facing
- Consider adding CLI command for get_stats if appropriate

### get_memory
**File:** `src/api/vault_connector.py:352`
**Module:** `src.api.vault_connector`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_memory if user-facing
- Consider adding CLI command for get_memory if appropriate

### create_memory
**File:** `src/api/vault_connector.py:384`
**Module:** `src.api.vault_connector`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_memory
- Consider adding UI control for create_memory if user-facing
- Consider adding CLI command for create_memory if appropriate

### update_memory
**File:** `src/api/vault_connector.py:413`
**Module:** `src.api.vault_connector`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_memory
- Consider adding UI control for update_memory if user-facing
- Consider adding CLI command for update_memory if appropriate

### delete_memory
**File:** `src/api/vault_connector.py:448`
**Module:** `src.api.vault_connector`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for delete_memory
- Consider adding UI control for delete_memory if user-facing
- Consider adding CLI command for delete_memory if appropriate

### get_audit_log
**File:** `src/api/vault_connector.py:470`
**Module:** `src.api.vault_connector`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_audit_log
- Consider adding UI control for get_audit_log if user-facing
- Consider adding CLI command for get_audit_log if appropriate

### create_backup
**File:** `src/api/vault_connector.py:510`
**Module:** `src.api.vault_connector`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_backup
- Consider adding UI control for create_backup if user-facing
- Consider adding CLI command for create_backup if appropriate

### get_status
**File:** `src/backend/alden_backend.py:531`
**Module:** `src.backend.alden_backend`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### get_or_create_context
**File:** `src/backend/alden_backend.py:462`
**Module:** `src.backend.alden_backend`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_or_create_context
- Consider adding UI control for get_or_create_context if user-facing
- Consider adding CLI command for get_or_create_context if appropriate

### create_alden_cli
**File:** `src/cli/alden_cli.py:389`
**Module:** `src.cli.alden_cli`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_alden_cli
- Consider adding UI control for create_alden_cli if user-facing
- Consider adding CLI command for create_alden_cli if appropriate

### get_app
**File:** `src/core/api.py:465`
**Module:** `src.core.api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_app
- Add Core interface control for get_app in CoreInterface.js
- Add core management CLI command for get_app

### create_session
**File:** `src/core/api.py:113`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Core interface control for create_session in CoreInterface.js

### get_session
**File:** `src/core/api.py:136`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Core interface control for get_session in CoreInterface.js

### get_active_sessions
**File:** `src/core/api.py:156`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for get_active_sessions in CoreInterface.js
- Add core management CLI command for get_active_sessions

### add_participant
**File:** `src/core/api.py:174`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for add_participant in CoreInterface.js
- Add core management CLI command for add_participant

### remove_participant
**File:** `src/core/api.py:194`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for remove_participant in CoreInterface.js
- Add core management CLI command for remove_participant

### get_session_participants
**File:** `src/core/api.py:214`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_session_participants
- Add Core interface control for get_session_participants in CoreInterface.js
- Add core management CLI command for get_session_participants

### start_turn_taking
**File:** `src/core/api.py:240`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for start_turn_taking in CoreInterface.js
- Add core management CLI command for start_turn_taking

### advance_turn
**File:** `src/core/api.py:260`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for advance_turn in CoreInterface.js
- Add core management CLI command for advance_turn

### create_breakout
**File:** `src/core/api.py:289`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for create_breakout in CoreInterface.js
- Add core management CLI command for create_breakout

### end_breakout
**File:** `src/core/api.py:309`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for end_breakout in CoreInterface.js
- Add core management CLI command for end_breakout

### share_insight
**File:** `src/core/api.py:329`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for share_insight in CoreInterface.js
- Add core management CLI command for share_insight

### export_session_log
**File:** `src/core/api.py:351`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for export_session_log in CoreInterface.js
- Add core management CLI command for export_session_log

### update_live_feed_settings
**File:** `src/core/api.py:371`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_live_feed_settings
- Add Core interface control for update_live_feed_settings in CoreInterface.js
- Add core management CLI command for update_live_feed_settings

### pause_session
**File:** `src/core/api.py:397`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for pause_session in CoreInterface.js
- Add core management CLI command for pause_session

### resume_session
**File:** `src/core/api.py:416`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for resume_session in CoreInterface.js
- Add core management CLI command for resume_session

### end_session
**File:** `src/core/api.py:435`
**Module:** `src.core.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for end_session in CoreInterface.js
- Add core management CLI command for end_session

### register_event_callback
**File:** `src/core/core.py:323`
**Module:** `src.core.core`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for register_event_callback
- Add Core interface control for register_event_callback in CoreInterface.js
- Add core management CLI command for register_event_callback

### create_session
**File:** `src/core/core.py:328`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Core interface control for create_session in CoreInterface.js

### add_participant
**File:** `src/core/core.py:402`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for add_participant in CoreInterface.js
- Add core management CLI command for add_participant

### remove_participant
**File:** `src/core/core.py:481`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for remove_participant in CoreInterface.js
- Add core management CLI command for remove_participant

### start_turn_taking
**File:** `src/core/core.py:544`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for start_turn_taking in CoreInterface.js
- Add core management CLI command for start_turn_taking

### advance_turn
**File:** `src/core/core.py:598`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for advance_turn in CoreInterface.js
- Add core management CLI command for advance_turn

### set_current_turn
**File:** `src/core/core.py:684`
**Module:** `src.core.core`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for set_current_turn
- Add Core interface control for set_current_turn in CoreInterface.js
- Add core management CLI command for set_current_turn

### create_breakout
**File:** `src/core/core.py:747`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for create_breakout in CoreInterface.js
- Add core management CLI command for create_breakout

### end_breakout
**File:** `src/core/core.py:810`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for end_breakout in CoreInterface.js
- Add core management CLI command for end_breakout

### share_insight
**File:** `src/core/core.py:929`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for share_insight in CoreInterface.js
- Add core management CLI command for share_insight

### get_session
**File:** `src/core/core.py:991`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Core interface control for get_session in CoreInterface.js

### get_active_sessions
**File:** `src/core/core.py:1005`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for get_active_sessions in CoreInterface.js
- Add core management CLI command for get_active_sessions

### pause_session
**File:** `src/core/core.py:1009`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for pause_session in CoreInterface.js
- Add core management CLI command for pause_session

### resume_session
**File:** `src/core/core.py:1026`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for resume_session in CoreInterface.js
- Add core management CLI command for resume_session

### end_session
**File:** `src/core/core.py:1043`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for end_session in CoreInterface.js
- Add core management CLI command for end_session

### export_session_log
**File:** `src/core/core.py:1070`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for export_session_log in CoreInterface.js
- Add core management CLI command for export_session_log

### get_session_summary
**File:** `src/core/core.py:1120`
**Module:** `src.core.core`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_session_summary
- Add Core interface control for get_session_summary in CoreInterface.js
- Add core management CLI command for get_session_summary

### record_metric
**File:** `src/core/core.py:1149`
**Module:** `src.core.core`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for record_metric
- Add Core interface control for record_metric in CoreInterface.js
- Add core management CLI command for record_metric

### start_operation_timer
**File:** `src/core/core.py:1354`
**Module:** `src.core.core`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_operation_timer
- Add Core interface control for start_operation_timer in CoreInterface.js
- Add core management CLI command for start_operation_timer

### end_operation_timer
**File:** `src/core/core.py:1359`
**Module:** `src.core.core`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for end_operation_timer
- Add Core interface control for end_operation_timer in CoreInterface.js
- Add core management CLI command for end_operation_timer

### get_performance_summary
**File:** `src/core/core.py:1390`
**Module:** `src.core.core`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for get_performance_summary in CoreInterface.js
- Add core management CLI command for get_performance_summary

### export_performance_data
**File:** `src/core/core.py:1437`
**Module:** `src.core.core`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_performance_data
- Add Core interface control for export_performance_data in CoreInterface.js
- Add core management CLI command for export_performance_data

### get_performance_trends
**File:** `src/core/core.py:1491`
**Module:** `src.core.core`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_performance_trends
- Add Core interface control for get_performance_trends in CoreInterface.js
- Add core management CLI command for get_performance_trends

### process_query_with_rag
**File:** `src/core/core.py:1525`
**Module:** `src.core.core`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Core interface control for process_query_with_rag in CoreInterface.js

### create_agentic_session
**File:** `src/core/enhanced_core.py:166`
**Module:** `src.core.enhanced_core`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_agentic_session
- Add Core interface control for create_agentic_session in CoreInterface.js
- Add core management CLI command for create_agentic_session

### execute_agentic_task
**File:** `src/core/enhanced_core.py:201`
**Module:** `src.core.enhanced_core`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_agentic_task
- Add Core interface control for execute_agentic_task in CoreInterface.js
- Add CLI command wrapper for execute_agentic_task

### delegate_to_optimal_agent
**File:** `src/core/enhanced_core.py:302`
**Module:** `src.core.enhanced_core`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for delegate_to_optimal_agent
- Add Core interface control for delegate_to_optimal_agent in CoreInterface.js
- Add core management CLI command for delegate_to_optimal_agent

### get_agent_capabilities_summary
**File:** `src/core/enhanced_core.py:433`
**Module:** `src.core.enhanced_core`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_capabilities_summary
- Add Core interface control for get_agent_capabilities_summary in CoreInterface.js
- Add core management CLI command for get_agent_capabilities_summary

### get_workflow_status_summary
**File:** `src/core/enhanced_core.py:449`
**Module:** `src.core.enhanced_core`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_workflow_status_summary
- Add Core interface control for get_workflow_status_summary in CoreInterface.js
- Add core management CLI command for get_workflow_status_summary

### get_enhanced_session_info
**File:** `src/core/enhanced_core.py:456`
**Module:** `src.core.enhanced_core`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_enhanced_session_info
- Add Core interface control for get_enhanced_session_info in CoreInterface.js
- Add core management CLI command for get_enhanced_session_info

### create_core_session
**File:** `src/core/enhanced_session_manager.py:85`
**Module:** `src.core.enhanced_session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_core_session
- Add Core interface control for create_core_session in CoreInterface.js
- Add core management CLI command for create_core_session

### add_participant
**File:** `src/core/enhanced_session_manager.py:183`
**Module:** `src.core.enhanced_session_manager`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for add_participant in CoreInterface.js
- Add core management CLI command for add_participant

### sync_agent_memory_to_communal
**File:** `src/core/enhanced_session_manager.py:255`
**Module:** `src.core.enhanced_session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for sync_agent_memory_to_communal
- Add Core interface control for sync_agent_memory_to_communal in CoreInterface.js
- Add core management CLI command for sync_agent_memory_to_communal

### create_breakout_room
**File:** `src/core/enhanced_session_manager.py:322`
**Module:** `src.core.enhanced_session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_breakout_room
- Add Core interface control for create_breakout_room in CoreInterface.js
- Add core management CLI command for create_breakout_room

### manage_turn_taking
**File:** `src/core/enhanced_session_manager.py:378`
**Module:** `src.core.enhanced_session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for manage_turn_taking
- Add Core interface control for manage_turn_taking in CoreInterface.js
- Add core management CLI command for manage_turn_taking

### get_session_performance_metrics
**File:** `src/core/enhanced_session_manager.py:456`
**Module:** `src.core.enhanced_session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_session_performance_metrics
- Add Core interface control for get_session_performance_metrics in CoreInterface.js
- Add core management CLI command for get_session_performance_metrics

### register_error_callback
**File:** `src/core/error_handling.py:181`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for register_error_callback
- Add Core interface control for register_error_callback in CoreInterface.js
- Add core management CLI command for register_error_callback

### register_recovery_strategy
**File:** `src/core/error_handling.py:185`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for register_recovery_strategy in CoreInterface.js
- Add core management CLI command for register_recovery_strategy

### handle_error
**File:** `src/core/error_handling.py:189`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for handle_error
- Add Core interface control for handle_error in CoreInterface.js
- Add core management CLI command for handle_error

### get_error_summary
**File:** `src/core/error_handling.py:280`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for get_error_summary in CoreInterface.js
- Add core management CLI command for get_error_summary

### reset_error_counts
**File:** `src/core/error_handling.py:288`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for reset_error_counts
- Add Core interface control for reset_error_counts in CoreInterface.js
- Add core management CLI command for reset_error_counts

### session_management_recovery
**File:** `src/core/error_handling.py:297`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for session_management_recovery in CoreInterface.js
- Add core management CLI command for session_management_recovery

### participant_management_recovery
**File:** `src/core/error_handling.py:308`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for participant_management_recovery in CoreInterface.js
- Add core management CLI command for participant_management_recovery

### turn_taking_recovery
**File:** `src/core/error_handling.py:316`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for turn_taking_recovery in CoreInterface.js
- Add core management CLI command for turn_taking_recovery

### vault_integration_recovery
**File:** `src/core/error_handling.py:324`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for vault_integration_recovery in CoreInterface.js
- Add core management CLI command for vault_integration_recovery

### system_recovery
**File:** `src/core/error_handling.py:332`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for system_recovery
- Add Core interface control for system_recovery in CoreInterface.js
- Add core management CLI command for system_recovery

### validate_session_id
**File:** `src/core/error_handling.py:343`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for validate_session_id in CoreInterface.js
- Add core management CLI command for validate_session_id

### validate_participant_data
**File:** `src/core/error_handling.py:354`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for validate_participant_data in CoreInterface.js
- Add core management CLI command for validate_participant_data

### validate_turn_order
**File:** `src/core/error_handling.py:372`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_turn_order
- Add Core interface control for validate_turn_order in CoreInterface.js
- Add core management CLI command for validate_turn_order

### validate_breakout_participants
**File:** `src/core/error_handling.py:381`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_breakout_participants
- Add Core interface control for validate_breakout_participants in CoreInterface.js
- Add core management CLI command for validate_breakout_participants

### record_error
**File:** `src/core/error_handling.py:396`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for record_error
- Add Core interface control for record_error in CoreInterface.js
- Add core management CLI command for record_error

### record_performance
**File:** `src/core/error_handling.py:408`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for record_performance in CoreInterface.js
- Add core management CLI command for record_performance

### get_error_rate
**File:** `src/core/error_handling.py:414`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_error_rate
- Add Core interface control for get_error_rate in CoreInterface.js
- Add core management CLI command for get_error_rate

### get_performance_summary
**File:** `src/core/error_handling.py:432`
**Module:** `src.core.error_handling`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for get_performance_summary in CoreInterface.js
- Add core management CLI command for get_performance_summary

### create_agentic_workflow
**File:** `src/core/kimi_k2_orchestration.py:207`
**Module:** `src.core.kimi_k2_orchestration`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_agentic_workflow
- Add Core interface control for create_agentic_workflow in CoreInterface.js
- Add core management CLI command for create_agentic_workflow

### execute_agentic_workflow
**File:** `src/core/kimi_k2_orchestration.py:264`
**Module:** `src.core.kimi_k2_orchestration`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_agentic_workflow
- Add Core interface control for execute_agentic_workflow in CoreInterface.js
- Add CLI command wrapper for execute_agentic_workflow

### get_agent_capabilities
**File:** `src/core/kimi_k2_orchestration.py:464`
**Module:** `src.core.kimi_k2_orchestration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_capabilities
- Add Core interface control for get_agent_capabilities in CoreInterface.js
- Add core management CLI command for get_agent_capabilities

### get_workflow_status
**File:** `src/core/kimi_k2_orchestration.py:468`
**Module:** `src.core.kimi_k2_orchestration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_workflow_status
- Add Core interface control for get_workflow_status in CoreInterface.js
- Add core management CLI command for get_workflow_status

### get_active_workflows
**File:** `src/core/kimi_k2_orchestration.py:473`
**Module:** `src.core.kimi_k2_orchestration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_active_workflows
- Add Core interface control for get_active_workflows in CoreInterface.js
- Add core management CLI command for get_active_workflows

### get_workflow_stats
**File:** `src/core/kimi_k2_orchestration.py:482`
**Module:** `src.core.kimi_k2_orchestration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_workflow_stats
- Add Core interface control for get_workflow_stats in CoreInterface.js
- Add core management CLI command for get_workflow_stats

### pause_workflow
**File:** `src/core/kimi_k2_orchestration.py:504`
**Module:** `src.core.kimi_k2_orchestration`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for pause_workflow
- Add Core interface control for pause_workflow in CoreInterface.js
- Add core management CLI command for pause_workflow

### resume_workflow
**File:** `src/core/kimi_k2_orchestration.py:509`
**Module:** `src.core.kimi_k2_orchestration`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for resume_workflow
- Add Core interface control for resume_workflow in CoreInterface.js
- Add core management CLI command for resume_workflow

### cancel_workflow
**File:** `src/core/kimi_k2_orchestration.py:518`
**Module:** `src.core.kimi_k2_orchestration`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for cancel_workflow
- Add Core interface control for cancel_workflow in CoreInterface.js
- Add core management CLI command for cancel_workflow

### create_core_logging_manager
**File:** `src/core/logging_manager.py:621`
**Module:** `src.core.logging_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_core_logging_manager
- Add Core interface control for create_core_logging_manager in CoreInterface.js
- Add core management CLI command for create_core_logging_manager

### log_session_event
**File:** `src/core/logging_manager.py:249`
**Module:** `src.core.logging_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_session_event
- Add Core interface control for log_session_event in CoreInterface.js
- Add core management CLI command for log_session_event

### log_participant_event
**File:** `src/core/logging_manager.py:300`
**Module:** `src.core.logging_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_participant_event
- Add Core interface control for log_participant_event in CoreInterface.js
- Add core management CLI command for log_participant_event

### log_performance_metric
**File:** `src/core/logging_manager.py:338`
**Module:** `src.core.logging_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_performance_metric
- Add Core interface control for log_performance_metric in CoreInterface.js
- Add core management CLI command for log_performance_metric

### log_audit_event
**File:** `src/core/logging_manager.py:374`
**Module:** `src.core.logging_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_audit_event
- Add Core interface control for log_audit_event in CoreInterface.js
- Add core management CLI command for log_audit_event

### log_error
**File:** `src/core/logging_manager.py:414`
**Module:** `src.core.logging_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for log_error in CoreInterface.js
- Add core management CLI command for log_error

### add_monitoring_callback
**File:** `src/core/logging_manager.py:456`
**Module:** `src.core.logging_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for add_monitoring_callback
- Add Core interface control for add_monitoring_callback in CoreInterface.js
- Add core management CLI command for add_monitoring_callback

### get_session_summary
**File:** `src/core/logging_manager.py:468`
**Module:** `src.core.logging_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_session_summary
- Add Core interface control for get_session_summary in CoreInterface.js
- Add core management CLI command for get_session_summary

### get_performance_summary
**File:** `src/core/logging_manager.py:483`
**Module:** `src.core.logging_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for get_performance_summary in CoreInterface.js
- Add core management CLI command for get_performance_summary

### get_audit_summary
**File:** `src/core/logging_manager.py:530`
**Module:** `src.core.logging_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for get_audit_summary in CoreInterface.js
- Add core management CLI command for get_audit_summary

### export_logs
**File:** `src/core/logging_manager.py:573`
**Module:** `src.core.logging_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_logs
- Add Core interface control for export_logs in CoreInterface.js
- Add core management CLI command for export_logs

### get_log_statistics
**File:** `src/core/logging_manager.py:599`
**Module:** `src.core.logging_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_log_statistics
- Add Core interface control for get_log_statistics in CoreInterface.js
- Add core management CLI command for get_log_statistics

### create_mimic_integration
**File:** `src/core/mimic_integration.py:709`
**Module:** `src.core.mimic_integration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_mimic_integration
- Add Core interface control for create_mimic_integration in CoreInterface.js
- Add core management CLI command for create_mimic_integration

### register_mimic_persona
**File:** `src/core/mimic_integration.py:137`
**Module:** `src.core.mimic_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for register_mimic_persona in CoreInterface.js
- Add core management CLI command for register_mimic_persona

### unregister_mimic_persona
**File:** `src/core/mimic_integration.py:157`
**Module:** `src.core.mimic_integration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for unregister_mimic_persona
- Add Core interface control for unregister_mimic_persona in CoreInterface.js
- Add core management CLI command for unregister_mimic_persona

### recommend_personas_for_session
**File:** `src/core/mimic_integration.py:178`
**Module:** `src.core.mimic_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for recommend_personas_for_session in CoreInterface.js
- Add core management CLI command for recommend_personas_for_session

### add_persona_to_session
**File:** `src/core/mimic_integration.py:351`
**Module:** `src.core.mimic_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for add_persona_to_session in CoreInterface.js
- Add core management CLI command for add_persona_to_session

### remove_persona_from_session
**File:** `src/core/mimic_integration.py:412`
**Module:** `src.core.mimic_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for remove_persona_from_session in CoreInterface.js
- Add core management CLI command for remove_persona_from_session

### share_insight_in_session
**File:** `src/core/mimic_integration.py:446`
**Module:** `src.core.mimic_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for share_insight_in_session in CoreInterface.js
- Add core management CLI command for share_insight_in_session

### record_session_performance
**File:** `src/core/mimic_integration.py:515`
**Module:** `src.core.mimic_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for record_session_performance in CoreInterface.js
- Add core management CLI command for record_session_performance

### get_session_insights
**File:** `src/core/mimic_integration.py:578`
**Module:** `src.core.mimic_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for get_session_insights in CoreInterface.js
- Add core management CLI command for get_session_insights

### get_session_performance_summary
**File:** `src/core/mimic_integration.py:594`
**Module:** `src.core.mimic_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for get_session_performance_summary in CoreInterface.js
- Add core management CLI command for get_session_performance_summary

### get_active_sessions
**File:** `src/core/mimic_integration.py:646`
**Module:** `src.core.mimic_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for get_active_sessions in CoreInterface.js
- Add core management CLI command for get_active_sessions

### get_integration_status
**File:** `src/core/mimic_integration.py:682`
**Module:** `src.core.mimic_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for get_integration_status in CoreInterface.js
- Add core management CLI command for get_integration_status

### get_session_manager
**File:** `src/core/session_manager.py:652`
**Module:** `src.core.session_manager`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Core interface control for get_session_manager in CoreInterface.js

### demo_session_management
**File:** `src/core/session_manager.py:660`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for demo_session_management
- Add Core interface control for demo_session_management in CoreInterface.js
- Add core management CLI command for demo_session_management

### create_session
**File:** `src/core/session_manager.py:107`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Core interface control for create_session in CoreInterface.js

### get_session
**File:** `src/core/session_manager.py:162`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Core interface control for get_session in CoreInterface.js

### update_session_activity
**File:** `src/core/session_manager.py:197`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_session_activity
- Add Core interface control for update_session_activity in CoreInterface.js
- Add core management CLI command for update_session_activity

### add_conversation_message
**File:** `src/core/session_manager.py:215`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Core interface control for add_conversation_message in CoreInterface.js

### get_conversation_history
**File:** `src/core/session_manager.py:346`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_conversation_history
- Add Core interface control for get_conversation_history in CoreInterface.js
- Add core management CLI command for get_conversation_history

### get_recent_context
**File:** `src/core/session_manager.py:379`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_recent_context
- Add Core interface control for get_recent_context in CoreInterface.js
- Add core management CLI command for get_recent_context

### extend_session
**File:** `src/core/session_manager.py:398`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for extend_session
- Add Core interface control for extend_session in CoreInterface.js
- Add core management CLI command for extend_session

### terminate_session
**File:** `src/core/session_manager.py:415`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for terminate_session
- Add Core interface control for terminate_session in CoreInterface.js
- Add core management CLI command for terminate_session

### get_user_sessions
**File:** `src/core/session_manager.py:458`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_user_sessions
- Add Core interface control for get_user_sessions in CoreInterface.js
- Add core management CLI command for get_user_sessions

### get_session_stats
**File:** `src/core/session_manager.py:473`
**Module:** `src.core.session_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_session_stats
- Add Core interface control for get_session_stats in CoreInterface.js
- Add core management CLI command for get_session_stats

### request_turn
**File:** `src/core/session_manager.py:489`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for request_turn
- Add Core interface control for request_turn in CoreInterface.js
- Add core management CLI command for request_turn

### release_turn
**File:** `src/core/session_manager.py:513`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for release_turn
- Add Core interface control for release_turn in CoreInterface.js
- Add core management CLI command for release_turn

### get_current_turn
**File:** `src/core/session_manager.py:535`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_current_turn
- Add Core interface control for get_current_turn in CoreInterface.js
- Add core management CLI command for get_current_turn

### propagate_context
**File:** `src/core/session_manager.py:542`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for propagate_context
- Add Core interface control for propagate_context in CoreInterface.js
- Add core management CLI command for propagate_context

### start_conversation
**File:** `src/core/session_manager.py:569`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_conversation
- Add Core interface control for start_conversation in CoreInterface.js
- Add core management CLI command for start_conversation

### send_user_message
**File:** `src/core/session_manager.py:591`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for send_user_message
- Add Core interface control for send_user_message in CoreInterface.js
- Add core management CLI command for send_user_message

### send_agent_response
**File:** `src/core/session_manager.py:609`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for send_agent_response
- Add Core interface control for send_agent_response in CoreInterface.js
- Add core management CLI command for send_agent_response

### get_conversation_summary
**File:** `src/core/session_manager.py:625`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_conversation_summary
- Add Core interface control for get_conversation_summary in CoreInterface.js
- Add core management CLI command for get_conversation_summary

### main
**File:** `src/core/session_manager.py:737`
**Module:** `src.core.session_manager`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Core interface control for main in CoreInterface.js

### create_alden_memory_manager
**File:** `src/database/alden_memory_manager.py:1169`
**Module:** `src.database.alden_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_alden_memory_manager
- Consider adding UI control for create_alden_memory_manager if user-facing
- Add database CLI command for create_alden_memory_manager in scripts/db_tools.py

### initialize
**File:** `src/database/alden_memory_manager.py:159`
**Module:** `src.database.alden_memory_manager`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for initialize if user-facing

### generate_memory_id
**File:** `src/database/alden_memory_manager.py:268`
**Module:** `src.database.alden_memory_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_memory_id
- Consider adding UI control for generate_memory_id if user-facing
- Add database CLI command for generate_memory_id in scripts/db_tools.py

### generate_session_id
**File:** `src/database/alden_memory_manager.py:272`
**Module:** `src.database.alden_memory_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_session_id
- Consider adding UI control for generate_session_id if user-facing
- Add database CLI command for generate_session_id in scripts/db_tools.py

### create_session
**File:** `src/database/alden_memory_manager.py:276`
**Module:** `src.database.alden_memory_manager`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for create_session if user-facing

### store_memory
**File:** `src/database/alden_memory_manager.py:353`
**Module:** `src.database.alden_memory_manager`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for store_memory if user-facing

### semantic_search
**File:** `src/database/alden_memory_manager.py:493`
**Module:** `src.database.alden_memory_manager`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for semantic_search if user-facing
- Add database CLI command for semantic_search in scripts/db_tools.py

### hybrid_search
**File:** `src/database/alden_memory_manager.py:619`
**Module:** `src.database.alden_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for hybrid_search
- Consider adding UI control for hybrid_search if user-facing
- Add database CLI command for hybrid_search in scripts/db_tools.py

### get_session_memories
**File:** `src/database/alden_memory_manager.py:748`
**Module:** `src.database.alden_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_session_memories
- Consider adding UI control for get_session_memories if user-facing
- Add database CLI command for get_session_memories in scripts/db_tools.py

### get_memory_statistics
**File:** `src/database/alden_memory_manager.py:849`
**Module:** `src.database.alden_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_memory_statistics
- Consider adding UI control for get_memory_statistics if user-facing
- Add database CLI command for get_memory_statistics in scripts/db_tools.py

### health_check
**File:** `src/database/alden_memory_manager.py:1070`
**Module:** `src.database.alden_memory_manager`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for health_check if user-facing

### main
**File:** `src/database/backup_manager.py:624`
**Module:** `src.database.backup_manager`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for main if user-facing

### create_backup
**File:** `src/database/backup_manager.py:105`
**Module:** `src.database.backup_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_backup
- Consider adding UI control for create_backup if user-facing
- Add database CLI command for create_backup in scripts/db_tools.py

### restore_backup
**File:** `src/database/backup_manager.py:349`
**Module:** `src.database.backup_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for restore_backup
- Consider adding UI control for restore_backup if user-facing
- Add database CLI command for restore_backup in scripts/db_tools.py

### list_backups
**File:** `src/database/backup_manager.py:579`
**Module:** `src.database.backup_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_backups
- Consider adding UI control for list_backups if user-facing
- Add database CLI command for list_backups in scripts/db_tools.py

### get_backup_status
**File:** `src/database/backup_manager.py:598`
**Module:** `src.database.backup_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_backup_status
- Consider adding UI control for get_backup_status if user-facing
- Add database CLI command for get_backup_status in scripts/db_tools.py

### get_database_manager
**File:** `src/database/database_manager.py:768`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for get_database_manager if user-facing

### initialize_database
**File:** `src/database/database_manager.py:777`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for initialize_database
- Consider adding UI control for initialize_database if user-facing
- Add database CLI command for initialize_database in scripts/db_tools.py

### get_schema_version_1
**File:** `src/database/database_manager.py:43`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_schema_version_1
- Consider adding UI control for get_schema_version_1 if user-facing
- Add database CLI command for get_schema_version_1 in scripts/db_tools.py

### get_connection
**File:** `src/database/database_manager.py:191`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_connection
- Consider adding UI control for get_connection if user-facing
- Add database CLI command for get_connection in scripts/db_tools.py

### initialize_schema
**File:** `src/database/database_manager.py:229`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for initialize_schema
- Consider adding UI control for initialize_schema if user-facing
- Add database CLI command for initialize_schema in scripts/db_tools.py

### get_schema_version
**File:** `src/database/database_manager.py:249`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for get_schema_version if user-facing

### transaction
**File:** `src/database/database_manager.py:261`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for transaction if user-facing
- Add database CLI command for transaction in scripts/db_tools.py

### create_user
**File:** `src/database/database_manager.py:272`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_user
- Consider adding UI control for create_user if user-facing
- Add database CLI command for create_user in scripts/db_tools.py

### get_user
**File:** `src/database/database_manager.py:288`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_user
- Consider adding UI control for get_user if user-facing
- Add database CLI command for get_user in scripts/db_tools.py

### get_user_by_username
**File:** `src/database/database_manager.py:304`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_user_by_username
- Consider adding UI control for get_user_by_username if user-facing
- Add database CLI command for get_user_by_username in scripts/db_tools.py

### update_user_preferences
**File:** `src/database/database_manager.py:320`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_user_preferences
- Consider adding UI control for update_user_preferences if user-facing
- Add database CLI command for update_user_preferences in scripts/db_tools.py

### update_username
**File:** `src/database/database_manager.py:328`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_username
- Consider adding UI control for update_username if user-facing
- Add database CLI command for update_username in scripts/db_tools.py

### create_agent
**File:** `src/database/database_manager.py:338`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for create_agent if user-facing
- Add database CLI command for create_agent in scripts/db_tools.py

### get_agent
**File:** `src/database/database_manager.py:363`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for get_agent if user-facing

### get_user_agents
**File:** `src/database/database_manager.py:380`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_user_agents
- Consider adding UI control for get_user_agents if user-facing
- Add database CLI command for get_user_agents in scripts/db_tools.py

### update_agent_activity
**File:** `src/database/database_manager.py:403`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_agent_activity
- Consider adding UI control for update_agent_activity if user-facing
- Add database CLI command for update_agent_activity in scripts/db_tools.py

### store_memory
**File:** `src/database/database_manager.py:415`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for store_memory if user-facing

### search_memories
**File:** `src/database/database_manager.py:440`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for search_memories
- Consider adding UI control for search_memories if user-facing
- Add database CLI command for search_memories in scripts/db_tools.py

### get_memory_stats
**File:** `src/database/database_manager.py:494`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_memory_stats
- Consider adding UI control for get_memory_stats if user-facing
- Add database CLI command for get_memory_stats in scripts/db_tools.py

### create_session
**File:** `src/database/database_manager.py:513`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for create_session if user-facing

### get_session
**File:** `src/database/database_manager.py:538`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for get_session if user-facing

### update_session_activity
**File:** `src/database/database_manager.py:556`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_session_activity
- Consider adding UI control for update_session_activity if user-facing
- Add database CLI command for update_session_activity in scripts/db_tools.py

### store_conversation
**File:** `src/database/database_manager.py:573`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for store_conversation
- Consider adding UI control for store_conversation if user-facing
- Add database CLI command for store_conversation in scripts/db_tools.py

### get_conversation_history
**File:** `src/database/database_manager.py:597`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_conversation_history
- Consider adding UI control for get_conversation_history if user-facing
- Add database CLI command for get_conversation_history in scripts/db_tools.py

### update_personality_trait
**File:** `src/database/database_manager.py:618`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_personality_trait
- Consider adding UI control for update_personality_trait if user-facing
- Add database CLI command for update_personality_trait in scripts/db_tools.py

### get_personality_profile
**File:** `src/database/database_manager.py:645`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_personality_profile
- Consider adding UI control for get_personality_profile if user-facing
- Add database CLI command for get_personality_profile in scripts/db_tools.py

### record_metric
**File:** `src/database/database_manager.py:667`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for record_metric
- Consider adding UI control for record_metric if user-facing
- Add database CLI command for record_metric in scripts/db_tools.py

### get_metrics
**File:** `src/database/database_manager.py:686`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_metrics
- Consider adding UI control for get_metrics if user-facing
- Add database CLI command for get_metrics in scripts/db_tools.py

### vacuum_database
**File:** `src/database/database_manager.py:717`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for vacuum_database
- Consider adding UI control for vacuum_database if user-facing
- Add database CLI command for vacuum_database in scripts/db_tools.py

### backup_database
**File:** `src/database/database_manager.py:724`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for backup_database
- Consider adding UI control for backup_database if user-facing
- Add database CLI command for backup_database in scripts/db_tools.py

### get_database_stats
**File:** `src/database/database_manager.py:740`
**Module:** `src.database.database_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_database_stats
- Consider adding UI control for get_database_stats if user-facing
- Add database CLI command for get_database_stats in scripts/db_tools.py

### create_long_term_memory_manager
**File:** `src/database/long_term_memory_manager.py:874`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_long_term_memory_manager
- Consider adding UI control for create_long_term_memory_manager if user-facing
- Add database CLI command for create_long_term_memory_manager in scripts/db_tools.py

### archive_memories_by_policy
**File:** `src/database/long_term_memory_manager.py:185`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for archive_memories_by_policy
- Consider adding UI control for archive_memories_by_policy if user-facing
- Add database CLI command for archive_memories_by_policy in scripts/db_tools.py

### create_manual_archive
**File:** `src/database/long_term_memory_manager.py:241`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_manual_archive
- Consider adding UI control for create_manual_archive if user-facing
- Add database CLI command for create_manual_archive in scripts/db_tools.py

### retrieve_from_archive
**File:** `src/database/long_term_memory_manager.py:306`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for retrieve_from_archive
- Consider adding UI control for retrieve_from_archive if user-facing
- Add database CLI command for retrieve_from_archive in scripts/db_tools.py

### optimize_session_cache
**File:** `src/database/long_term_memory_manager.py:380`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for optimize_session_cache
- Consider adding UI control for optimize_session_cache if user-facing
- Add database CLI command for optimize_session_cache in scripts/db_tools.py

### get_session_cache
**File:** `src/database/long_term_memory_manager.py:423`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_session_cache
- Consider adding UI control for get_session_cache if user-facing
- Add database CLI command for get_session_cache in scripts/db_tools.py

### consolidate_similar_memories
**File:** `src/database/long_term_memory_manager.py:457`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for consolidate_similar_memories
- Consider adding UI control for consolidate_similar_memories if user-facing
- Add database CLI command for consolidate_similar_memories in scripts/db_tools.py

### get_consolidation_clusters
**File:** `src/database/long_term_memory_manager.py:513`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_consolidation_clusters
- Consider adding UI control for get_consolidation_clusters if user-facing
- Add database CLI command for get_consolidation_clusters in scripts/db_tools.py

### build_memory_hierarchy
**File:** `src/database/long_term_memory_manager.py:552`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for build_memory_hierarchy
- Consider adding UI control for build_memory_hierarchy if user-facing
- Add database CLI command for build_memory_hierarchy in scripts/db_tools.py

### get_memory_hierarchy
**File:** `src/database/long_term_memory_manager.py:590`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_memory_hierarchy
- Consider adding UI control for get_memory_hierarchy if user-facing
- Add database CLI command for get_memory_hierarchy in scripts/db_tools.py

### analyze_session_patterns
**File:** `src/database/long_term_memory_manager.py:639`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for analyze_session_patterns
- Consider adding UI control for analyze_session_patterns if user-facing
- Add database CLI command for analyze_session_patterns in scripts/db_tools.py

### get_session_patterns
**File:** `src/database/long_term_memory_manager.py:677`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_session_patterns
- Consider adding UI control for get_session_patterns if user-facing
- Add database CLI command for get_session_patterns in scripts/db_tools.py

### get_long_term_utilization
**File:** `src/database/long_term_memory_manager.py:718`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_long_term_utilization
- Consider adding UI control for get_long_term_utilization if user-facing
- Add database CLI command for get_long_term_utilization in scripts/db_tools.py

### get_optimization_insights
**File:** `src/database/long_term_memory_manager.py:774`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_optimization_insights
- Consider adding UI control for get_optimization_insights if user-facing
- Add database CLI command for get_optimization_insights in scripts/db_tools.py

### get_long_term_statistics
**File:** `src/database/long_term_memory_manager.py:827`
**Module:** `src.database.long_term_memory_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_long_term_statistics
- Consider adding UI control for get_long_term_statistics if user-facing
- Add database CLI command for get_long_term_statistics in scripts/db_tools.py

### apply_migration_v11
**File:** `src/database/migration_v1_1.py:235`
**Module:** `src.database.migration_v1_1`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for apply_migration_v11
- Consider adding UI control for apply_migration_v11 if user-facing
- Add database CLI command for apply_migration_v11 in scripts/db_tools.py

### apply_migration
**File:** `src/database/migration_v1_1.py:24`
**Module:** `src.database.migration_v1_1`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for apply_migration
- Consider adding UI control for apply_migration if user-facing
- Add database CLI command for apply_migration in scripts/db_tools.py

### rollback_migration
**File:** `src/database/migration_v1_1.py:206`
**Module:** `src.database.migration_v1_1`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for rollback_migration
- Consider adding UI control for rollback_migration if user-facing
- Add database CLI command for rollback_migration in scripts/db_tools.py

### connect
**File:** `src/database/pgvector_client.py:97`
**Module:** `src.database.pgvector_client`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for connect if user-facing

### disconnect
**File:** `src/database/pgvector_client.py:140`
**Module:** `src.database.pgvector_client`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for disconnect
- Consider adding UI control for disconnect if user-facing
- Add database CLI command for disconnect in scripts/db_tools.py

### store_memory_slice
**File:** `src/database/pgvector_client.py:147`
**Module:** `src.database.pgvector_client`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for store_memory_slice
- Consider adding UI control for store_memory_slice if user-facing
- Add database CLI command for store_memory_slice in scripts/db_tools.py

### semantic_search
**File:** `src/database/pgvector_client.py:198`
**Module:** `src.database.pgvector_client`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for semantic_search if user-facing
- Add database CLI command for semantic_search in scripts/db_tools.py

### hybrid_search
**File:** `src/database/pgvector_client.py:299`
**Module:** `src.database.pgvector_client`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for hybrid_search
- Consider adding UI control for hybrid_search if user-facing
- Add database CLI command for hybrid_search in scripts/db_tools.py

### store_reasoning_chain
**File:** `src/database/pgvector_client.py:409`
**Module:** `src.database.pgvector_client`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for store_reasoning_chain
- Consider adding UI control for store_reasoning_chain if user-facing
- Add database CLI command for store_reasoning_chain in scripts/db_tools.py

### get_memory_statistics
**File:** `src/database/pgvector_client.py:455`
**Module:** `src.database.pgvector_client`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_memory_statistics
- Consider adding UI control for get_memory_statistics if user-facing
- Add database CLI command for get_memory_statistics in scripts/db_tools.py

### health_check
**File:** `src/database/pgvector_client.py:540`
**Module:** `src.database.pgvector_client`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for health_check if user-facing

### get_statistics
**File:** `src/embedding/semantic_embedding_service.py:347`
**Module:** `src.embedding.semantic_embedding_service`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_statistics
- Consider adding UI control for get_statistics if user-facing
- Consider adding CLI command for get_statistics if appropriate

### get_comprehensive_statistics
**File:** `src/embedding/semantic_embedding_service.py:568`
**Module:** `src.embedding.semantic_embedding_service`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_comprehensive_statistics
- Consider adding UI control for get_comprehensive_statistics if user-facing
- Consider adding CLI command for get_comprehensive_statistics if appropriate

### create_llm_selection_layer
**File:** `src/llm/llm_selection_layer.py:721`
**Module:** `src.llm.llm_selection_layer`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_llm_selection_layer
- Consider adding UI control for create_llm_selection_layer if user-facing
- Consider adding CLI command for create_llm_selection_layer if appropriate

### get_current_model_info
**File:** `src/llm/llm_selection_layer.py:605`
**Module:** `src.llm.llm_selection_layer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_current_model_info
- Consider adding UI control for get_current_model_info if user-facing
- Consider adding CLI command for get_current_model_info if appropriate

### get_available_models
**File:** `src/llm/llm_selection_layer.py:611`
**Module:** `src.llm.llm_selection_layer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_available_models
- Consider adding UI control for get_available_models if user-facing
- Consider adding CLI command for get_available_models if appropriate

### get_model_performance_stats
**File:** `src/llm/llm_selection_layer.py:615`
**Module:** `src.llm.llm_selection_layer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_model_performance_stats
- Consider adding UI control for get_model_performance_stats if user-facing
- Consider adding CLI command for get_model_performance_stats if appropriate

### get_swap_history
**File:** `src/llm/llm_selection_layer.py:621`
**Module:** `src.llm.llm_selection_layer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_swap_history
- Consider adding UI control for get_swap_history if user-facing
- Consider adding CLI command for get_swap_history if appropriate

### get_status
**File:** `src/llm/llm_selection_layer.py:676`
**Module:** `src.llm.llm_selection_layer`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### create_llm_client
**File:** `src/llm/local_llm_client.py:759`
**Module:** `src.llm.local_llm_client`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_llm_client
- Consider adding UI control for create_llm_client if user-facing
- Consider adding CLI command for create_llm_client if appropriate

### get_connection
**File:** `src/llm/local_llm_client.py:192`
**Module:** `src.llm.local_llm_client`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_connection
- Consider adding UI control for get_connection if user-facing
- Consider adding CLI command for get_connection if appropriate

### get_pool_stats
**File:** `src/llm/local_llm_client.py:248`
**Module:** `src.llm.local_llm_client`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_pool_stats
- Consider adding UI control for get_pool_stats if user-facing
- Consider adding CLI command for get_pool_stats if appropriate

### get_status
**File:** `src/llm/local_llm_client.py:717`
**Module:** `src.llm.local_llm_client`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### get_token_tracker
**File:** `src/log_handling/agent_token_tracker.py:465`
**Module:** `src.log_handling.agent_token_tracker`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_token_tracker
- Consider adding UI control for get_token_tracker if user-facing
- Consider adding CLI command for get_token_tracker if appropriate

### get_agent_performance_metrics
**File:** `src/log_handling/agent_token_tracker.py:505`
**Module:** `src.log_handling.agent_token_tracker`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_performance_metrics
- Consider adding UI control for get_agent_performance_metrics if user-facing
- Consider adding CLI command for get_agent_performance_metrics if appropriate

### get_compliance_report
**File:** `src/log_handling/agent_token_tracker.py:519`
**Module:** `src.log_handling.agent_token_tracker`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_compliance_report
- Consider adding UI control for get_compliance_report if user-facing
- Consider adding CLI command for get_compliance_report if appropriate

### update_metrics
**File:** `src/log_handling/agent_token_tracker.py:79`
**Module:** `src.log_handling.agent_token_tracker`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_metrics
- Consider adding UI control for update_metrics if user-facing
- Consider adding CLI command for update_metrics if appropriate

### get_agent_metrics
**File:** `src/log_handling/agent_token_tracker.py:236`
**Module:** `src.log_handling.agent_token_tracker`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_metrics
- Consider adding UI control for get_agent_metrics if user-facing
- Consider adding CLI command for get_agent_metrics if appropriate

### get_usage_summary
**File:** `src/log_handling/agent_token_tracker.py:258`
**Module:** `src.log_handling.agent_token_tracker`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_usage_summary
- Consider adding UI control for get_usage_summary if user-facing
- Consider adding CLI command for get_usage_summary if appropriate

### get_claude_integration_compliance_report
**File:** `src/log_handling/agent_token_tracker.py:317`
**Module:** `src.log_handling.agent_token_tracker`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_claude_integration_compliance_report
- Consider adding UI control for get_claude_integration_compliance_report if user-facing
- Consider adding CLI command for get_claude_integration_compliance_report if appropriate

### get_log_file_path
**File:** `src/log_handling/agent_token_tracker.py:442`
**Module:** `src.log_handling.agent_token_tracker`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_log_file_path
- Consider adding UI control for get_log_file_path if user-facing
- Consider adding CLI command for get_log_file_path if appropriate

### get_system_status
**File:** `src/log_handling/agent_token_tracker.py:446`
**Module:** `src.log_handling.agent_token_tracker`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_system_status if user-facing
- Consider adding CLI command for get_system_status if appropriate

### get_instance
**File:** `src/log_handling/exception_handler.py:165`
**Module:** `src.log_handling.exception_handler`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_instance
- Consider adding UI control for get_instance if user-facing
- Consider adding CLI command for get_instance if appropriate

### get_log_file_path
**File:** `src/log_handling/exception_handler.py:377`
**Module:** `src.log_handling.exception_handler`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_log_file_path
- Consider adding UI control for get_log_file_path if user-facing
- Consider adding CLI command for get_log_file_path if appropriate

### get_memory_usage_stats
**File:** `src/memory/memory_pruning_manager.py:534`
**Module:** `src.memory.memory_pruning_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_memory_usage_stats
- Consider adding UI control for get_memory_usage_stats if user-facing
- Consider adding CLI command for get_memory_usage_stats if appropriate

### create_alden_persona
**File:** `src/personas/alden.py:1661`
**Module:** `src.personas.alden`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_alden_persona
- Consider adding UI control for create_alden_persona if user-facing
- Consider adding CLI command for create_alden_persona if appropriate

### generate_response
**File:** `src/personas/alden.py:611`
**Module:** `src.personas.alden`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_response
- Consider adding UI control for generate_response if user-facing
- Consider adding CLI command for generate_response if appropriate

### update_trait
**File:** `src/personas/alden.py:922`
**Module:** `src.personas.alden`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_trait
- Consider adding UI control for update_trait if user-facing
- Consider adding CLI command for update_trait if appropriate

### add_correction_event
**File:** `src/personas/alden.py:994`
**Module:** `src.personas.alden`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for add_correction_event
- Consider adding UI control for add_correction_event if user-facing
- Consider adding CLI command for add_correction_event if appropriate

### record_session_mood
**File:** `src/personas/alden.py:1083`
**Module:** `src.personas.alden`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for record_session_mood
- Consider adding UI control for record_session_mood if user-facing
- Consider adding CLI command for record_session_mood if appropriate

### export_memory
**File:** `src/personas/alden.py:1169`
**Module:** `src.personas.alden`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_memory
- Consider adding UI control for export_memory if user-facing
- Consider adding CLI command for export_memory if appropriate

### get_status
**File:** `src/personas/alden.py:1217`
**Module:** `src.personas.alden`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### optimize_self
**File:** `src/personas/alden.py:1265`
**Module:** `src.personas.alden`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for optimize_self
- Consider adding UI control for optimize_self if user-facing
- Consider adding CLI command for optimize_self if appropriate

### check_ecosystem_health
**File:** `src/personas/alden.py:1318`
**Module:** `src.personas.alden`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_ecosystem_health
- Consider adding UI control for check_ecosystem_health if user-facing
- Consider adding CLI command for check_ecosystem_health if appropriate

### store_conversation_memory
**File:** `src/personas/alden.py:1430`
**Module:** `src.personas.alden`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for store_conversation_memory
- Consider adding UI control for store_conversation_memory if user-facing
- Consider adding CLI command for store_conversation_memory if appropriate

### retrieve_similar_memories
**File:** `src/personas/alden.py:1489`
**Module:** `src.personas.alden`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for retrieve_similar_memories
- Consider adding UI control for retrieve_similar_memories if user-facing
- Consider adding CLI command for retrieve_similar_memories if appropriate

### generate_reasoning_chain
**File:** `src/personas/alden.py:1549`
**Module:** `src.personas.alden`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_reasoning_chain
- Consider adding UI control for generate_reasoning_chain if user-facing
- Consider adding CLI command for generate_reasoning_chain if appropriate

### get_enhanced_memory_statistics
**File:** `src/personas/alden.py:1616`
**Module:** `src.personas.alden`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_enhanced_memory_statistics
- Consider adding UI control for get_enhanced_memory_statistics if user-facing
- Consider adding CLI command for get_enhanced_memory_statistics if appropriate

### create_alden_semantic_adapter
**File:** `src/personas/alden_semantic_adapter.py:728`
**Module:** `src.personas.alden_semantic_adapter`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_alden_semantic_adapter
- Consider adding UI control for create_alden_semantic_adapter if user-facing
- Consider adding CLI command for create_alden_semantic_adapter if appropriate

### initialize_semantic_manager
**File:** `src/personas/alden_semantic_adapter.py:112`
**Module:** `src.personas.alden_semantic_adapter`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for initialize_semantic_manager
- Consider adding UI control for initialize_semantic_manager if user-facing
- Consider adding CLI command for initialize_semantic_manager if appropriate

### generate_enhanced_response
**File:** `src/personas/alden_semantic_adapter.py:337`
**Module:** `src.personas.alden_semantic_adapter`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_enhanced_response
- Consider adding UI control for generate_enhanced_response if user-facing
- Consider adding CLI command for generate_enhanced_response if appropriate

### get_semantic_statistics
**File:** `src/personas/alden_semantic_adapter.py:590`
**Module:** `src.personas.alden_semantic_adapter`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_semantic_statistics
- Consider adding UI control for get_semantic_statistics if user-facing
- Consider adding CLI command for get_semantic_statistics if appropriate

### health_check
**File:** `src/personas/alden_semantic_adapter.py:640`
**Module:** `src.personas.alden_semantic_adapter`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for health_check if user-facing

### generate
**File:** `src/personas/alden_semantic_adapter.py:792`
**Module:** `src.personas.alden_semantic_adapter`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for generate if user-facing

### get_status
**File:** `src/personas/alden_semantic_adapter.py:802`
**Module:** `src.personas.alden_semantic_adapter`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### create_mimic_persona
**File:** `src/personas/mimic.py:1237`
**Module:** `src.personas.mimic`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_mimic_persona
- Consider adding UI control for create_mimic_persona if user-facing
- Consider adding CLI command for create_mimic_persona if appropriate

### get_performance_analytics
**File:** `src/personas/mimic.py:974`
**Module:** `src.personas.mimic`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_performance_analytics if user-facing
- Consider adding CLI command for get_performance_analytics if appropriate

### get_performance_tier
**File:** `src/personas/mimic.py:1086`
**Module:** `src.personas.mimic`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_performance_tier if user-facing
- Consider adding CLI command for get_performance_tier if appropriate

### get_status
**File:** `src/personas/mimic.py:1211`
**Module:** `src.personas.mimic`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### create_memory_sync_service
**File:** `src/services/memory_sync_service.py:1060`
**Module:** `src.services.memory_sync_service`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_memory_sync_service
- Consider adding UI control for create_memory_sync_service if user-facing
- Consider adding CLI command for create_memory_sync_service if appropriate

### get_agent_memory_slice
**File:** `src/services/memory_sync_service.py:553`
**Module:** `src.services.memory_sync_service`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_memory_slice
- Consider adding UI control for get_agent_memory_slice if user-facing
- Consider adding CLI command for get_agent_memory_slice if appropriate

### get_sync_statistics
**File:** `src/services/memory_sync_service.py:658`
**Module:** `src.services.memory_sync_service`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_sync_statistics
- Consider adding UI control for get_sync_statistics if user-facing
- Consider adding CLI command for get_sync_statistics if appropriate

### get_session_memories
**File:** `src/services/memory_sync_service.py:1112`
**Module:** `src.services.memory_sync_service`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_session_memories
- Consider adding UI control for get_session_memories if user-facing
- Consider adding CLI command for get_session_memories if appropriate

### create_multi_agent_coordinator
**File:** `src/services/multi_agent_memory_coordinator.py:804`
**Module:** `src.services.multi_agent_memory_coordinator`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_multi_agent_coordinator
- Consider adding UI control for create_multi_agent_coordinator if user-facing
- Consider adding CLI command for create_multi_agent_coordinator if appropriate

### get_memory_allocation
**File:** `src/services/multi_agent_memory_coordinator.py:579`
**Module:** `src.services.multi_agent_memory_coordinator`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_memory_allocation
- Consider adding UI control for get_memory_allocation if user-facing
- Consider adding CLI command for get_memory_allocation if appropriate

### get_coordinator_status
**File:** `src/services/multi_agent_memory_coordinator.py:631`
**Module:** `src.services.multi_agent_memory_coordinator`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_coordinator_status
- Consider adding UI control for get_coordinator_status if user-facing
- Consider adding CLI command for get_coordinator_status if appropriate

### get_handoff_manager
**File:** `src/synapse/agent_handoff.py:721`
**Module:** `src.synapse.agent_handoff`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for get_handoff_manager in SynapseGateway.js

### demo_agent_handoff
**File:** `src/synapse/agent_handoff.py:729`
**Module:** `src.synapse.agent_handoff`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for demo_agent_handoff
- Add Synapse interface control for demo_agent_handoff in SynapseGateway.js
- Consider adding CLI command for demo_agent_handoff if appropriate

### initiate_handoff
**File:** `src/synapse/agent_handoff.py:111`
**Module:** `src.synapse.agent_handoff`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for initiate_handoff in SynapseGateway.js

### hydrate_target_agent_context
**File:** `src/synapse/agent_handoff.py:486`
**Module:** `src.synapse.agent_handoff`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for hydrate_target_agent_context in SynapseGateway.js

### get_handoff_status
**File:** `src/synapse/agent_handoff.py:665`
**Module:** `src.synapse.agent_handoff`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for get_handoff_status in SynapseGateway.js

### cancel_handoff
**File:** `src/synapse/agent_handoff.py:669`
**Module:** `src.synapse.agent_handoff`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for cancel_handoff
- Add Synapse interface control for cancel_handoff in SynapseGateway.js
- Consider adding CLI command for cancel_handoff if appropriate

### get_agent_capabilities
**File:** `src/synapse/agent_handoff.py:685`
**Module:** `src.synapse.agent_handoff`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_capabilities
- Add Synapse interface control for get_agent_capabilities in SynapseGateway.js
- Consider adding CLI command for get_agent_capabilities if appropriate

### list_active_handoffs
**File:** `src/synapse/agent_handoff.py:689`
**Module:** `src.synapse.agent_handoff`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_active_handoffs
- Add Synapse interface control for list_active_handoffs in SynapseGateway.js
- Consider adding CLI command for list_active_handoffs if appropriate

### get_handoff_history
**File:** `src/synapse/agent_handoff.py:703`
**Module:** `src.synapse.agent_handoff`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_handoff_history
- Add Synapse interface control for get_handoff_history in SynapseGateway.js
- Consider adding CLI command for get_handoff_history if appropriate

### main
**File:** `src/synapse/agent_handoff.py:890`
**Module:** `src.synapse.agent_handoff`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for main in SynapseGateway.js

### get_synapse
**File:** `src/synapse/api.py:120`
**Module:** `src.synapse.api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_synapse
- Add Synapse interface control for get_synapse in SynapseGateway.js
- Consider adding CLI command for get_synapse if appropriate

### get_handoff_manager
**File:** `src/synapse/api.py:126`
**Module:** `src.synapse.api`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for get_handoff_manager in SynapseGateway.js

### get_current_user
**File:** `src/synapse/api.py:132`
**Module:** `src.synapse.api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_current_user
- Add Synapse interface control for get_current_user in SynapseGateway.js
- Consider adding CLI command for get_current_user if appropriate

### initialize_synapse
**File:** `src/synapse/api.py:140`
**Module:** `src.synapse.api`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for initialize_synapse
- Add Synapse interface control for initialize_synapse in SynapseGateway.js
- Consider adding CLI command for initialize_synapse if appropriate

### register_plugin
**File:** `src/synapse/api.py:151`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for register_plugin in SynapseGateway.js
- Consider adding CLI command for register_plugin if appropriate

### approve_plugin
**File:** `src/synapse/api.py:173`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for approve_plugin in SynapseGateway.js
- Consider adding CLI command for approve_plugin if appropriate

### revoke_plugin
**File:** `src/synapse/api.py:198`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for revoke_plugin
- Add Synapse interface control for revoke_plugin in SynapseGateway.js
- Consider adding CLI command for revoke_plugin if appropriate

### execute_plugin
**File:** `src/synapse/api.py:223`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for execute_plugin in SynapseGateway.js
- Add CLI command wrapper for execute_plugin

### get_plugin_status
**File:** `src/synapse/api.py:254`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_plugin_status
- Add Synapse interface control for get_plugin_status in SynapseGateway.js
- Consider adding CLI command for get_plugin_status if appropriate

### list_plugins
**File:** `src/synapse/api.py:275`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_plugins
- Add Synapse interface control for list_plugins in SynapseGateway.js
- Consider adding CLI command for list_plugins if appropriate

### request_permissions
**File:** `src/synapse/api.py:295`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for request_permissions
- Add Synapse interface control for request_permissions in SynapseGateway.js
- Consider adding CLI command for request_permissions if appropriate

### approve_permissions
**File:** `src/synapse/api.py:317`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for approve_permissions
- Add Synapse interface control for approve_permissions in SynapseGateway.js
- Consider adding CLI command for approve_permissions if appropriate

### deny_permissions
**File:** `src/synapse/api.py:340`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for deny_permissions
- Add Synapse interface control for deny_permissions in SynapseGateway.js
- Consider adding CLI command for deny_permissions if appropriate

### get_pending_permissions
**File:** `src/synapse/api.py:363`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_pending_permissions
- Add Synapse interface control for get_pending_permissions in SynapseGateway.js
- Consider adding CLI command for get_pending_permissions if appropriate

### request_connection
**File:** `src/synapse/api.py:382`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for request_connection in SynapseGateway.js
- Consider adding CLI command for request_connection if appropriate

### approve_connection
**File:** `src/synapse/api.py:403`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for approve_connection in SynapseGateway.js
- Consider adding CLI command for approve_connection if appropriate

### close_connection
**File:** `src/synapse/api.py:422`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for close_connection in SynapseGateway.js
- Consider adding CLI command for close_connection if appropriate

### get_connections
**File:** `src/synapse/api.py:444`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_connections
- Add Synapse interface control for get_connections in SynapseGateway.js
- Consider adding CLI command for get_connections if appropriate

### get_webhooks
**File:** `src/synapse/api.py:462`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_webhooks
- Add Synapse interface control for get_webhooks in SynapseGateway.js
- Consider adding CLI command for get_webhooks if appropriate

### create_webhook
**File:** `src/synapse/api.py:488`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_webhook
- Add Synapse interface control for create_webhook in SynapseGateway.js
- Consider adding CLI command for create_webhook if appropriate

### run_benchmark
**File:** `src/synapse/api.py:514`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for run_benchmark
- Add Synapse interface control for run_benchmark in SynapseGateway.js
- Consider adding CLI command for run_benchmark if appropriate

### get_benchmark_summary
**File:** `src/synapse/api.py:542`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_benchmark_summary
- Add Synapse interface control for get_benchmark_summary in SynapseGateway.js
- Consider adding CLI command for get_benchmark_summary if appropriate

### get_traffic_logs
**File:** `src/synapse/api.py:569`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_traffic_logs
- Add Synapse interface control for get_traffic_logs in SynapseGateway.js
- Consider adding CLI command for get_traffic_logs if appropriate

### get_traffic_summary
**File:** `src/synapse/api.py:587`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_traffic_summary
- Add Synapse interface control for get_traffic_summary in SynapseGateway.js
- Consider adding CLI command for get_traffic_summary if appropriate

### export_traffic_logs
**File:** `src/synapse/api.py:605`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_traffic_logs
- Add Synapse interface control for export_traffic_logs in SynapseGateway.js
- Consider adding CLI command for export_traffic_logs if appropriate

### get_system_status
**File:** `src/synapse/api.py:629`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_system_status in SynapseGateway.js
- Consider adding CLI command for get_system_status if appropriate

### export_system_data
**File:** `src/synapse/api.py:646`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_system_data
- Add Synapse interface control for export_system_data in SynapseGateway.js
- Consider adding CLI command for export_system_data if appropriate

### save_settings
**File:** `src/synapse/api.py:686`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for save_settings
- Add Synapse interface control for save_settings in SynapseGateway.js
- Consider adding CLI command for save_settings if appropriate

### get_settings
**File:** `src/synapse/api.py:712`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_settings
- Add Synapse interface control for get_settings in SynapseGateway.js
- Consider adding CLI command for get_settings if appropriate

### health_check
**File:** `src/synapse/api.py:745`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for health_check in SynapseGateway.js

### initiate_handoff
**File:** `src/synapse/api.py:756`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for initiate_handoff in SynapseGateway.js

### get_handoff_status
**File:** `src/synapse/api.py:796`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for get_handoff_status in SynapseGateway.js

### cancel_handoff
**File:** `src/synapse/api.py:828`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for cancel_handoff
- Add Synapse interface control for cancel_handoff in SynapseGateway.js
- Consider adding CLI command for cancel_handoff if appropriate

### list_active_handoffs
**File:** `src/synapse/api.py:850`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_active_handoffs
- Add Synapse interface control for list_active_handoffs in SynapseGateway.js
- Consider adding CLI command for list_active_handoffs if appropriate

### get_handoff_history
**File:** `src/synapse/api.py:867`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_handoff_history
- Add Synapse interface control for get_handoff_history in SynapseGateway.js
- Consider adding CLI command for get_handoff_history if appropriate

### get_agent_capabilities
**File:** `src/synapse/api.py:885`
**Module:** `src.synapse.api`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_capabilities
- Add Synapse interface control for get_agent_capabilities in SynapseGateway.js
- Consider adding CLI command for get_agent_capabilities if appropriate

### get_audit_logger
**File:** `src/synapse/audit_logger.py:527`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_audit_logger
- Add Synapse interface control for get_audit_logger in SynapseGateway.js
- Consider adding CLI command for get_audit_logger if appropriate

### log_outbound_request
**File:** `src/synapse/audit_logger.py:532`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for log_outbound_request in SynapseGateway.js
- Consider adding CLI command for log_outbound_request if appropriate

### log_agent_interaction
**File:** `src/synapse/audit_logger.py:544`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for log_agent_interaction in SynapseGateway.js
- Consider adding CLI command for log_agent_interaction if appropriate

### log_permission_check
**File:** `src/synapse/audit_logger.py:553`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for log_permission_check in SynapseGateway.js
- Consider adding CLI command for log_permission_check if appropriate

### log_security_violation
**File:** `src/synapse/audit_logger.py:562`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for log_security_violation in SynapseGateway.js
- Consider adding CLI command for log_security_violation if appropriate

### log_event
**File:** `src/synapse/audit_logger.py:179`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_event
- Add Synapse interface control for log_event in SynapseGateway.js
- Consider adding CLI command for log_event if appropriate

### log_outbound_request
**File:** `src/synapse/audit_logger.py:245`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for log_outbound_request in SynapseGateway.js
- Consider adding CLI command for log_outbound_request if appropriate

### log_agent_interaction
**File:** `src/synapse/audit_logger.py:282`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for log_agent_interaction in SynapseGateway.js
- Consider adding CLI command for log_agent_interaction if appropriate

### log_permission_check
**File:** `src/synapse/audit_logger.py:310`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for log_permission_check in SynapseGateway.js
- Consider adding CLI command for log_permission_check if appropriate

### log_rate_limit
**File:** `src/synapse/audit_logger.py:334`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_rate_limit
- Add Synapse interface control for log_rate_limit in SynapseGateway.js
- Consider adding CLI command for log_rate_limit if appropriate

### log_security_violation
**File:** `src/synapse/audit_logger.py:360`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for log_security_violation in SynapseGateway.js
- Consider adding CLI command for log_security_violation if appropriate

### log_browser_preview
**File:** `src/synapse/audit_logger.py:377`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for log_browser_preview in SynapseGateway.js
- Consider adding CLI command for log_browser_preview if appropriate

### log_webhook_config
**File:** `src/synapse/audit_logger.py:401`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for log_webhook_config in SynapseGateway.js
- Consider adding CLI command for log_webhook_config if appropriate

### get_audit_summary
**File:** `src/synapse/audit_logger.py:423`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_audit_summary in SynapseGateway.js
- Consider adding CLI command for get_audit_summary if appropriate

### verify_log_integrity
**File:** `src/synapse/audit_logger.py:481`
**Module:** `src.synapse.audit_logger`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for verify_log_integrity in SynapseGateway.js
- Consider adding CLI command for verify_log_integrity if appropriate

### start_benchmark
**File:** `src/synapse/benchmark.py:106`
**Module:** `src.synapse.benchmark`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_benchmark
- Add Synapse interface control for start_benchmark in SynapseGateway.js
- Consider adding CLI command for start_benchmark if appropriate

### complete_benchmark
**File:** `src/synapse/benchmark.py:149`
**Module:** `src.synapse.benchmark`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for complete_benchmark
- Add Synapse interface control for complete_benchmark in SynapseGateway.js
- Consider adding CLI command for complete_benchmark if appropriate

### run_benchmark
**File:** `src/synapse/benchmark.py:197`
**Module:** `src.synapse.benchmark`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for run_benchmark
- Add Synapse interface control for run_benchmark in SynapseGateway.js
- Consider adding CLI command for run_benchmark if appropriate

### get_benchmark_summary
**File:** `src/synapse/benchmark.py:252`
**Module:** `src.synapse.benchmark`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_benchmark_summary
- Add Synapse interface control for get_benchmark_summary in SynapseGateway.js
- Consider adding CLI command for get_benchmark_summary if appropriate

### get_recent_benchmarks
**File:** `src/synapse/benchmark.py:256`
**Module:** `src.synapse.benchmark`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_recent_benchmarks
- Add Synapse interface control for get_recent_benchmarks in SynapseGateway.js
- Consider adding CLI command for get_recent_benchmarks if appropriate

### get_performance_tier
**File:** `src/synapse/benchmark.py:271`
**Module:** `src.synapse.benchmark`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_performance_tier in SynapseGateway.js
- Consider adding CLI command for get_performance_tier if appropriate

### get_risk_score
**File:** `src/synapse/benchmark.py:279`
**Module:** `src.synapse.benchmark`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_risk_score
- Add Synapse interface control for get_risk_score in SynapseGateway.js
- Consider adding CLI command for get_risk_score if appropriate

### list_benchmarked_plugins
**File:** `src/synapse/benchmark.py:287`
**Module:** `src.synapse.benchmark`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_benchmarked_plugins
- Add Synapse interface control for list_benchmarked_plugins in SynapseGateway.js
- Consider adding CLI command for list_benchmarked_plugins if appropriate

### export_benchmark_data
**File:** `src/synapse/benchmark.py:291`
**Module:** `src.synapse.benchmark`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_benchmark_data
- Add Synapse interface control for export_benchmark_data in SynapseGateway.js
- Consider adding CLI command for export_benchmark_data if appropriate

### create_browser_session
**File:** `src/synapse/browser_preview.py:381`
**Module:** `src.synapse.browser_preview`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for create_browser_session in SynapseGateway.js
- Consider adding CLI command for create_browser_session if appropriate

### preview_url
**File:** `src/synapse/browser_preview.py:386`
**Module:** `src.synapse.browser_preview`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for preview_url in SynapseGateway.js
- Consider adding CLI command for preview_url if appropriate

### get_session_info
**File:** `src/synapse/browser_preview.py:392`
**Module:** `src.synapse.browser_preview`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_session_info in SynapseGateway.js
- Consider adding CLI command for get_session_info if appropriate

### get_policy
**File:** `src/synapse/browser_preview.py:85`
**Module:** `src.synapse.browser_preview`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_policy in SynapseGateway.js
- Consider adding CLI command for get_policy if appropriate

### validate_url
**File:** `src/synapse/browser_preview.py:107`
**Module:** `src.synapse.browser_preview`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for validate_url in SynapseGateway.js
- Consider adding CLI command for validate_url if appropriate

### sanitize_html
**File:** `src/synapse/browser_preview.py:149`
**Module:** `src.synapse.browser_preview`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for sanitize_html in SynapseGateway.js
- Consider adding CLI command for sanitize_html if appropriate

### create_session
**File:** `src/synapse/browser_preview.py:201`
**Module:** `src.synapse.browser_preview`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for create_session in SynapseGateway.js

### preview_url
**File:** `src/synapse/browser_preview.py:216`
**Module:** `src.synapse.browser_preview`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for preview_url in SynapseGateway.js
- Consider adding CLI command for preview_url if appropriate

### get_session_info
**File:** `src/synapse/browser_preview.py:341`
**Module:** `src.synapse.browser_preview`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_session_info in SynapseGateway.js
- Consider adding CLI command for get_session_info if appropriate

### block_domain
**File:** `src/synapse/browser_preview.py:370`
**Module:** `src.synapse.browser_preview`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for block_domain
- Add Synapse interface control for block_domain in SynapseGateway.js
- Consider adding CLI command for block_domain if appropriate

### create_agent_browser_session
**File:** `src/synapse/browser_preview_integration.py:352`
**Module:** `src.synapse.browser_preview_integration`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for create_agent_browser_session in SynapseGateway.js
- Consider adding CLI command for create_agent_browser_session if appropriate

### preview_url_for_agent
**File:** `src/synapse/browser_preview_integration.py:357`
**Module:** `src.synapse.browser_preview_integration`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for preview_url_for_agent in SynapseGateway.js
- Consider adding CLI command for preview_url_for_agent if appropriate

### start_live_preview_for_agent
**File:** `src/synapse/browser_preview_integration.py:363`
**Module:** `src.synapse.browser_preview_integration`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_live_preview_for_agent
- Add Synapse interface control for start_live_preview_for_agent in SynapseGateway.js
- Consider adding CLI command for start_live_preview_for_agent if appropriate

### stop_live_preview
**File:** `src/synapse/browser_preview_integration.py:368`
**Module:** `src.synapse.browser_preview_integration`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for stop_live_preview in SynapseGateway.js
- Consider adding CLI command for stop_live_preview if appropriate

### get_agent_session_info
**File:** `src/synapse/browser_preview_integration.py:373`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_agent_session_info in SynapseGateway.js
- Consider adding CLI command for get_agent_session_info if appropriate

### get_whitelist_status
**File:** `src/synapse/browser_preview_integration.py:378`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_whitelist_status in SynapseGateway.js
- Consider adding CLI command for get_whitelist_status if appropriate

### add_allowed_domain
**File:** `src/synapse/browser_preview_integration.py:383`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for add_allowed_domain in SynapseGateway.js
- Consider adding CLI command for add_allowed_domain if appropriate

### remove_allowed_domain
**File:** `src/synapse/browser_preview_integration.py:388`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for remove_allowed_domain in SynapseGateway.js
- Consider adding CLI command for remove_allowed_domain if appropriate

### is_url_allowed
**File:** `src/synapse/browser_preview_integration.py:87`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for is_url_allowed in SynapseGateway.js
- Consider adding CLI command for is_url_allowed if appropriate

### add_allowed_domain
**File:** `src/synapse/browser_preview_integration.py:115`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for add_allowed_domain in SynapseGateway.js
- Consider adding CLI command for add_allowed_domain if appropriate

### remove_allowed_domain
**File:** `src/synapse/browser_preview_integration.py:121`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for remove_allowed_domain in SynapseGateway.js
- Consider adding CLI command for remove_allowed_domain if appropriate

### add_blocked_domain
**File:** `src/synapse/browser_preview_integration.py:127`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for add_blocked_domain in SynapseGateway.js
- Consider adding CLI command for add_blocked_domain if appropriate

### remove_blocked_domain
**File:** `src/synapse/browser_preview_integration.py:133`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for remove_blocked_domain
- Add Synapse interface control for remove_blocked_domain in SynapseGateway.js
- Consider adding CLI command for remove_blocked_domain if appropriate

### start_live_preview
**File:** `src/synapse/browser_preview_integration.py:149`
**Module:** `src.synapse.browser_preview_integration`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for start_live_preview in SynapseGateway.js
- Consider adding CLI command for start_live_preview if appropriate

### stop_live_preview
**File:** `src/synapse/browser_preview_integration.py:172`
**Module:** `src.synapse.browser_preview_integration`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for stop_live_preview in SynapseGateway.js
- Consider adding CLI command for stop_live_preview if appropriate

### get_active_previews
**File:** `src/synapse/browser_preview_integration.py:211`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_active_previews
- Add Synapse interface control for get_active_previews in SynapseGateway.js
- Consider adding CLI command for get_active_previews if appropriate

### create_agent_session
**File:** `src/synapse/browser_preview_integration.py:241`
**Module:** `src.synapse.browser_preview_integration`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for create_agent_session in SynapseGateway.js
- Consider adding CLI command for create_agent_session if appropriate

### preview_url_for_agent
**File:** `src/synapse/browser_preview_integration.py:248`
**Module:** `src.synapse.browser_preview_integration`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for preview_url_for_agent in SynapseGateway.js
- Consider adding CLI command for preview_url_for_agent if appropriate

### start_live_preview_for_agent
**File:** `src/synapse/browser_preview_integration.py:275`
**Module:** `src.synapse.browser_preview_integration`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_live_preview_for_agent
- Add Synapse interface control for start_live_preview_for_agent in SynapseGateway.js
- Consider adding CLI command for start_live_preview_for_agent if appropriate

### stop_live_preview
**File:** `src/synapse/browser_preview_integration.py:284`
**Module:** `src.synapse.browser_preview_integration`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for stop_live_preview in SynapseGateway.js
- Consider adding CLI command for stop_live_preview if appropriate

### get_agent_session_info
**File:** `src/synapse/browser_preview_integration.py:288`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_agent_session_info in SynapseGateway.js
- Consider adding CLI command for get_agent_session_info if appropriate

### get_all_session_info
**File:** `src/synapse/browser_preview_integration.py:296`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_all_session_info
- Add Synapse interface control for get_all_session_info in SynapseGateway.js
- Consider adding CLI command for get_all_session_info if appropriate

### get_whitelist_status
**File:** `src/synapse/browser_preview_integration.py:303`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_whitelist_status in SynapseGateway.js
- Consider adding CLI command for get_whitelist_status if appropriate

### add_allowed_domain
**File:** `src/synapse/browser_preview_integration.py:312`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for add_allowed_domain in SynapseGateway.js
- Consider adding CLI command for add_allowed_domain if appropriate

### remove_allowed_domain
**File:** `src/synapse/browser_preview_integration.py:316`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for remove_allowed_domain in SynapseGateway.js
- Consider adding CLI command for remove_allowed_domain if appropriate

### add_blocked_domain
**File:** `src/synapse/browser_preview_integration.py:320`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for add_blocked_domain in SynapseGateway.js
- Consider adding CLI command for add_blocked_domain if appropriate

### remove_blocked_domain
**File:** `src/synapse/browser_preview_integration.py:324`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for remove_blocked_domain
- Add Synapse interface control for remove_blocked_domain in SynapseGateway.js
- Consider adding CLI command for remove_blocked_domain if appropriate

### get_live_previews
**File:** `src/synapse/browser_preview_integration.py:328`
**Module:** `src.synapse.browser_preview_integration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_live_previews
- Add Synapse interface control for get_live_previews in SynapseGateway.js
- Consider adding CLI command for get_live_previews if appropriate

### create_browser_preview_ui
**File:** `src/synapse/browser_preview_ui.py:435`
**Module:** `src.synapse.browser_preview_ui`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_browser_preview_ui
- Add Synapse interface control for create_browser_preview_ui in SynapseGateway.js
- Consider adding CLI command for create_browser_preview_ui if appropriate

### destroy
**File:** `src/synapse/browser_preview_ui.py:425`
**Module:** `src.synapse.browser_preview_ui`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for destroy in SynapseGateway.js
- Consider adding CLI command for destroy if appropriate

### create_claude_gateway
**File:** `src/synapse/claude_gateway.py:588`
**Module:** `src.synapse.claude_gateway`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_claude_gateway
- Add Synapse interface control for create_claude_gateway in SynapseGateway.js
- Consider adding CLI command for create_claude_gateway if appropriate

### prompt_must_not_be_empty
**File:** `src/synapse/claude_gateway.py:61`
**Module:** `src.synapse.claude_gateway`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for prompt_must_not_be_empty
- Add Synapse interface control for prompt_must_not_be_empty in SynapseGateway.js
- Consider adding CLI command for prompt_must_not_be_empty if appropriate

### agent_id_must_be_valid
**File:** `src/synapse/claude_gateway.py:67`
**Module:** `src.synapse.claude_gateway`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for agent_id_must_be_valid
- Add Synapse interface control for agent_id_must_be_valid in SynapseGateway.js
- Consider adding CLI command for agent_id_must_be_valid if appropriate

### run
**File:** `src/synapse/claude_gateway.py:564`
**Module:** `src.synapse.claude_gateway`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for run in SynapseGateway.js

### security_middleware
**File:** `src/synapse/claude_gateway.py:167`
**Module:** `src.synapse.claude_gateway`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for security_middleware
- Add Synapse interface control for security_middleware in SynapseGateway.js
- Consider adding CLI command for security_middleware if appropriate

### health_check
**File:** `src/synapse/claude_gateway.py:205`
**Module:** `src.synapse.claude_gateway`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for health_check in SynapseGateway.js

### validate_claude_request
**File:** `src/synapse/claude_gateway.py:218`
**Module:** `src.synapse.claude_gateway`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_claude_request
- Add Synapse interface control for validate_claude_request in SynapseGateway.js
- Consider adding CLI command for validate_claude_request if appropriate

### append_to_vault
**File:** `src/synapse/claude_gateway.py:294`
**Module:** `src.synapse.claude_gateway`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for append_to_vault
- Add Synapse interface control for append_to_vault in SynapseGateway.js
- Consider adding CLI command for append_to_vault if appropriate

### process_claude_directive
**File:** `src/synapse/claude_gateway.py:354`
**Module:** `src.synapse.claude_gateway`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for process_claude_directive
- Add Synapse interface control for process_claude_directive in SynapseGateway.js
- Add CLI command wrapper for process_claude_directive

### to_dict
**File:** `src/synapse/config.py:77`
**Module:** `src.synapse.config`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for to_dict
- Add Synapse interface control for to_dict in SynapseGateway.js
- Consider adding CLI command for to_dict if appropriate

### from_dict
**File:** `src/synapse/config.py:94`
**Module:** `src.synapse.config`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for from_dict
- Add Synapse interface control for from_dict in SynapseGateway.js
- Consider adding CLI command for from_dict if appropriate

### load_config
**File:** `src/synapse/config.py:122`
**Module:** `src.synapse.config`
**Type:** function
**Missing:** test, ui_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for load_config
- Add Synapse interface control for load_config in SynapseGateway.js

### save_config
**File:** `src/synapse/config.py:147`
**Module:** `src.synapse.config`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for save_config
- Add Synapse interface control for save_config in SynapseGateway.js
- Consider adding CLI command for save_config if appropriate

### create_default_config
**File:** `src/synapse/config.py:171`
**Module:** `src.synapse.config`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_default_config
- Add Synapse interface control for create_default_config in SynapseGateway.js
- Consider adding CLI command for create_default_config if appropriate

### validate_config
**File:** `src/synapse/config.py:181`
**Module:** `src.synapse.config`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for validate_config in SynapseGateway.js

### get_environment_config
**File:** `src/synapse/config.py:230`
**Module:** `src.synapse.config`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_environment_config
- Add Synapse interface control for get_environment_config in SynapseGateway.js
- Consider adding CLI command for get_environment_config if appropriate

### merge_configs
**File:** `src/synapse/config.py:268`
**Module:** `src.synapse.config`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for merge_configs
- Add Synapse interface control for merge_configs in SynapseGateway.js
- Consider adding CLI command for merge_configs if appropriate

### add_credential
**File:** `src/synapse/credential_manager.py:529`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for add_credential
- Add Synapse interface control for add_credential in SynapseGateway.js
- Consider adding CLI command for add_credential if appropriate

### get_credential
**File:** `src/synapse/credential_manager.py:536`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_credential
- Add Synapse interface control for get_credential in SynapseGateway.js
- Consider adding CLI command for get_credential if appropriate

### get_credential_password
**File:** `src/synapse/credential_manager.py:541`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_credential_password
- Add Synapse interface control for get_credential_password in SynapseGateway.js
- Consider adding CLI command for get_credential_password if appropriate

### search_credentials
**File:** `src/synapse/credential_manager.py:546`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for search_credentials
- Add Synapse interface control for search_credentials in SynapseGateway.js
- Consider adding CLI command for search_credentials if appropriate

### request_injection
**File:** `src/synapse/credential_manager.py:553`
**Module:** `src.synapse.credential_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for request_injection
- Add Synapse interface control for request_injection in SynapseGateway.js
- Consider adding CLI command for request_injection if appropriate

### approve_injection
**File:** `src/synapse/credential_manager.py:559`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for approve_injection
- Add Synapse interface control for approve_injection in SynapseGateway.js
- Consider adding CLI command for approve_injection if appropriate

### execute_injection
**File:** `src/synapse/credential_manager.py:564`
**Module:** `src.synapse.credential_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_injection
- Add Synapse interface control for execute_injection in SynapseGateway.js
- Add CLI command wrapper for execute_injection

### encrypt
**File:** `src/synapse/credential_manager.py:94`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for encrypt in SynapseGateway.js

### decrypt
**File:** `src/synapse/credential_manager.py:98`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for decrypt in SynapseGateway.js

### get_master_key
**File:** `src/synapse/credential_manager.py:102`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_master_key
- Add Synapse interface control for get_master_key in SynapseGateway.js
- Consider adding CLI command for get_master_key if appropriate

### add_credential
**File:** `src/synapse/credential_manager.py:191`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for add_credential
- Add Synapse interface control for add_credential in SynapseGateway.js
- Consider adding CLI command for add_credential if appropriate

### update_credential
**File:** `src/synapse/credential_manager.py:217`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_credential
- Add Synapse interface control for update_credential in SynapseGateway.js
- Consider adding CLI command for update_credential if appropriate

### delete_credential
**File:** `src/synapse/credential_manager.py:244`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for delete_credential
- Add Synapse interface control for delete_credential in SynapseGateway.js
- Consider adding CLI command for delete_credential if appropriate

### get_credential
**File:** `src/synapse/credential_manager.py:255`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_credential
- Add Synapse interface control for get_credential in SynapseGateway.js
- Consider adding CLI command for get_credential if appropriate

### get_credential_password
**File:** `src/synapse/credential_manager.py:289`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_credential_password
- Add Synapse interface control for get_credential_password in SynapseGateway.js
- Consider adding CLI command for get_credential_password if appropriate

### search_credentials
**File:** `src/synapse/credential_manager.py:312`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for search_credentials
- Add Synapse interface control for search_credentials in SynapseGateway.js
- Consider adding CLI command for search_credentials if appropriate

### request_injection
**File:** `src/synapse/credential_manager.py:350`
**Module:** `src.synapse.credential_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for request_injection
- Add Synapse interface control for request_injection in SynapseGateway.js
- Consider adding CLI command for request_injection if appropriate

### approve_injection
**File:** `src/synapse/credential_manager.py:383`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for approve_injection
- Add Synapse interface control for approve_injection in SynapseGateway.js
- Consider adding CLI command for approve_injection if appropriate

### deny_injection
**File:** `src/synapse/credential_manager.py:396`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for deny_injection
- Add Synapse interface control for deny_injection in SynapseGateway.js
- Consider adding CLI command for deny_injection if appropriate

### execute_injection
**File:** `src/synapse/credential_manager.py:410`
**Module:** `src.synapse.credential_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_injection
- Add Synapse interface control for execute_injection in SynapseGateway.js
- Add CLI command wrapper for execute_injection

### get_pending_injections
**File:** `src/synapse/credential_manager.py:480`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_pending_injections
- Add Synapse interface control for get_pending_injections in SynapseGateway.js
- Consider adding CLI command for get_pending_injections if appropriate

### get_injection_history
**File:** `src/synapse/credential_manager.py:487`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_injection_history
- Add Synapse interface control for get_injection_history in SynapseGateway.js
- Consider adding CLI command for get_injection_history if appropriate

### add_domain_mapping
**File:** `src/synapse/credential_manager.py:496`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for add_domain_mapping
- Add Synapse interface control for add_domain_mapping in SynapseGateway.js
- Consider adding CLI command for add_domain_mapping if appropriate

### get_related_domains
**File:** `src/synapse/credential_manager.py:501`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_related_domains
- Add Synapse interface control for get_related_domains in SynapseGateway.js
- Consider adding CLI command for get_related_domains if appropriate

### validate_credential
**File:** `src/synapse/credential_manager.py:505`
**Module:** `src.synapse.credential_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_credential
- Add Synapse interface control for validate_credential in SynapseGateway.js
- Consider adding CLI command for validate_credential if appropriate

### to_dict
**File:** `src/synapse/manifest.py:76`
**Module:** `src.synapse.manifest`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for to_dict
- Add Synapse interface control for to_dict in SynapseGateway.js
- Consider adding CLI command for to_dict if appropriate

### to_json
**File:** `src/synapse/manifest.py:84`
**Module:** `src.synapse.manifest`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for to_json
- Add Synapse interface control for to_json in SynapseGateway.js
- Consider adding CLI command for to_json if appropriate

### calculate_signature
**File:** `src/synapse/manifest.py:88`
**Module:** `src.synapse.manifest`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for calculate_signature
- Add Synapse interface control for calculate_signature in SynapseGateway.js
- Consider adding CLI command for calculate_signature if appropriate

### validate_signature
**File:** `src/synapse/manifest.py:103`
**Module:** `src.synapse.manifest`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_signature
- Add Synapse interface control for validate_signature in SynapseGateway.js
- Consider adding CLI command for validate_signature if appropriate

### validate_manifest
**File:** `src/synapse/manifest.py:122`
**Module:** `src.synapse.manifest`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_manifest
- Add Synapse interface control for validate_manifest in SynapseGateway.js
- Consider adding CLI command for validate_manifest if appropriate

### create_manifest
**File:** `src/synapse/manifest.py:209`
**Module:** `src.synapse.manifest`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_manifest
- Add Synapse interface control for create_manifest in SynapseGateway.js
- Consider adding CLI command for create_manifest if appropriate

### load_manifest_from_json
**File:** `src/synapse/manifest.py:241`
**Module:** `src.synapse.manifest`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for load_manifest_from_json
- Add Synapse interface control for load_manifest_from_json in SynapseGateway.js
- Consider adding CLI command for load_manifest_from_json if appropriate

### execute_filesystem_mcp
**File:** `src/synapse/mcp_executor.py:28`
**Module:** `src.synapse.mcp_executor`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_filesystem_mcp
- Add Synapse interface control for execute_filesystem_mcp in SynapseGateway.js
- Add CLI command wrapper for execute_filesystem_mcp

### execute_github_mcp
**File:** `src/synapse/mcp_executor.py:50`
**Module:** `src.synapse.mcp_executor`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_github_mcp
- Add Synapse interface control for execute_github_mcp in SynapseGateway.js
- Add CLI command wrapper for execute_github_mcp

### execute_gmail_calendar_mcp
**File:** `src/synapse/mcp_executor.py:96`
**Module:** `src.synapse.mcp_executor`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_gmail_calendar_mcp
- Add Synapse interface control for execute_gmail_calendar_mcp in SynapseGateway.js
- Add CLI command wrapper for execute_gmail_calendar_mcp

### initialize_mcp_plugin_manager
**File:** `src/synapse/mcp_plugin_manager.py:366`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for initialize_mcp_plugin_manager
- Add Synapse interface control for initialize_mcp_plugin_manager in SynapseGateway.js
- Consider adding CLI command for initialize_mcp_plugin_manager if appropriate

### get_mcp_plugin_manager
**File:** `src/synapse/mcp_plugin_manager.py:373`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_mcp_plugin_manager
- Add Synapse interface control for get_mcp_plugin_manager in SynapseGateway.js
- Consider adding CLI command for get_mcp_plugin_manager if appropriate

### initialize
**File:** `src/synapse/mcp_plugin_manager.py:57`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** async_function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for initialize in SynapseGateway.js

### load_server_registry
**File:** `src/synapse/mcp_plugin_manager.py:77`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for load_server_registry
- Add Synapse interface control for load_server_registry in SynapseGateway.js
- Consider adding CLI command for load_server_registry if appropriate

### create_default_registry
**File:** `src/synapse/mcp_plugin_manager.py:92`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_default_registry
- Add Synapse interface control for create_default_registry in SynapseGateway.js
- Consider adding CLI command for create_default_registry if appropriate

### discover_mcp_plugins
**File:** `src/synapse/mcp_plugin_manager.py:112`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for discover_mcp_plugins
- Add Synapse interface control for discover_mcp_plugins in SynapseGateway.js
- Consider adding CLI command for discover_mcp_plugins if appropriate

### register_plugin_from_manifest
**File:** `src/synapse/mcp_plugin_manager.py:130`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for register_plugin_from_manifest
- Add Synapse interface control for register_plugin_from_manifest in SynapseGateway.js
- Consider adding CLI command for register_plugin_from_manifest if appropriate

### validate_mcp_manifest
**File:** `src/synapse/mcp_plugin_manager.py:173`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_mcp_manifest
- Add Synapse interface control for validate_mcp_manifest in SynapseGateway.js
- Consider adding CLI command for validate_mcp_manifest if appropriate

### auto_start_servers
**File:** `src/synapse/mcp_plugin_manager.py:188`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for auto_start_servers
- Add Synapse interface control for auto_start_servers in SynapseGateway.js
- Consider adding CLI command for auto_start_servers if appropriate

### start_mcp_server
**File:** `src/synapse/mcp_plugin_manager.py:204`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_mcp_server
- Add Synapse interface control for start_mcp_server in SynapseGateway.js
- Consider adding CLI command for start_mcp_server if appropriate

### stop_mcp_server
**File:** `src/synapse/mcp_plugin_manager.py:237`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for stop_mcp_server
- Add Synapse interface control for stop_mcp_server in SynapseGateway.js
- Consider adding CLI command for stop_mcp_server if appropriate

### execute_mcp_tool
**File:** `src/synapse/mcp_plugin_manager.py:267`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_mcp_tool
- Add Synapse interface control for execute_mcp_tool in SynapseGateway.js
- Add CLI command wrapper for execute_mcp_tool

### get_server_info
**File:** `src/synapse/mcp_plugin_manager.py:294`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_server_info
- Add Synapse interface control for get_server_info in SynapseGateway.js
- Consider adding CLI command for get_server_info if appropriate

### list_active_servers
**File:** `src/synapse/mcp_plugin_manager.py:298`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_active_servers
- Add Synapse interface control for list_active_servers in SynapseGateway.js
- Consider adding CLI command for list_active_servers if appropriate

### get_available_tools
**File:** `src/synapse/mcp_plugin_manager.py:302`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_available_tools
- Add Synapse interface control for get_available_tools in SynapseGateway.js
- Consider adding CLI command for get_available_tools if appropriate

### health_check_all_servers
**File:** `src/synapse/mcp_plugin_manager.py:309`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for health_check_all_servers
- Add Synapse interface control for health_check_all_servers in SynapseGateway.js
- Consider adding CLI command for health_check_all_servers if appropriate

### update_server_registry
**File:** `src/synapse/mcp_plugin_manager.py:332`
**Module:** `src.synapse.mcp_plugin_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_server_registry
- Add Synapse interface control for update_server_registry in SynapseGateway.js
- Consider adding CLI command for update_server_registry if appropriate

### request_permissions
**File:** `src/synapse/permissions.py:82`
**Module:** `src.synapse.permissions`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for request_permissions
- Add Synapse interface control for request_permissions in SynapseGateway.js
- Consider adding CLI command for request_permissions if appropriate

### approve_permissions
**File:** `src/synapse/permissions.py:125`
**Module:** `src.synapse.permissions`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for approve_permissions
- Add Synapse interface control for approve_permissions in SynapseGateway.js
- Consider adding CLI command for approve_permissions if appropriate

### deny_permissions
**File:** `src/synapse/permissions.py:167`
**Module:** `src.synapse.permissions`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for deny_permissions
- Add Synapse interface control for deny_permissions in SynapseGateway.js
- Consider adding CLI command for deny_permissions if appropriate

### revoke_permissions
**File:** `src/synapse/permissions.py:194`
**Module:** `src.synapse.permissions`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for revoke_permissions
- Add Synapse interface control for revoke_permissions in SynapseGateway.js
- Consider adding CLI command for revoke_permissions if appropriate

### check_permission
**File:** `src/synapse/permissions.py:231`
**Module:** `src.synapse.permissions`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for check_permission in SynapseGateway.js
- Consider adding CLI command for check_permission if appropriate

### get_plugin_permissions
**File:** `src/synapse/permissions.py:252`
**Module:** `src.synapse.permissions`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_plugin_permissions
- Add Synapse interface control for get_plugin_permissions in SynapseGateway.js
- Consider adding CLI command for get_plugin_permissions if appropriate

### get_pending_requests
**File:** `src/synapse/permissions.py:274`
**Module:** `src.synapse.permissions`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_pending_requests
- Add Synapse interface control for get_pending_requests in SynapseGateway.js
- Consider adding CLI command for get_pending_requests if appropriate

### get_plugin_grants
**File:** `src/synapse/permissions.py:279`
**Module:** `src.synapse.permissions`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_plugin_grants
- Add Synapse interface control for get_plugin_grants in SynapseGateway.js
- Consider adding CLI command for get_plugin_grants if appropriate

### export_permissions
**File:** `src/synapse/permissions.py:319`
**Module:** `src.synapse.permissions`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_permissions
- Add Synapse interface control for export_permissions in SynapseGateway.js
- Consider adding CLI command for export_permissions if appropriate

### import_permissions
**File:** `src/synapse/permissions.py:327`
**Module:** `src.synapse.permissions`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for import_permissions
- Add Synapse interface control for import_permissions in SynapseGateway.js
- Consider adding CLI command for import_permissions if appropriate

### register_plugin
**File:** `src/synapse/plugin_manager.py:105`
**Module:** `src.synapse.plugin_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for register_plugin in SynapseGateway.js
- Consider adding CLI command for register_plugin if appropriate

### approve_plugin
**File:** `src/synapse/plugin_manager.py:156`
**Module:** `src.synapse.plugin_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for approve_plugin in SynapseGateway.js
- Consider adding CLI command for approve_plugin if appropriate

### revoke_plugin
**File:** `src/synapse/plugin_manager.py:215`
**Module:** `src.synapse.plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for revoke_plugin
- Add Synapse interface control for revoke_plugin in SynapseGateway.js
- Consider adding CLI command for revoke_plugin if appropriate

### execute_plugin
**File:** `src/synapse/plugin_manager.py:274`
**Module:** `src.synapse.plugin_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for execute_plugin in SynapseGateway.js
- Add CLI command wrapper for execute_plugin

### get_plugin_status
**File:** `src/synapse/plugin_manager.py:443`
**Module:** `src.synapse.plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_plugin_status
- Add Synapse interface control for get_plugin_status in SynapseGateway.js
- Consider adding CLI command for get_plugin_status if appropriate

### list_plugins
**File:** `src/synapse/plugin_manager.py:447`
**Module:** `src.synapse.plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_plugins
- Add Synapse interface control for list_plugins in SynapseGateway.js
- Consider adding CLI command for list_plugins if appropriate

### get_plugin_manifest
**File:** `src/synapse/plugin_manager.py:456`
**Module:** `src.synapse.plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_plugin_manifest
- Add Synapse interface control for get_plugin_manifest in SynapseGateway.js
- Consider adding CLI command for get_plugin_manifest if appropriate

### export_plugin_data
**File:** `src/synapse/plugin_manager.py:460`
**Module:** `src.synapse.plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_plugin_data
- Add Synapse interface control for export_plugin_data in SynapseGateway.js
- Consider adding CLI command for export_plugin_data if appropriate

### add_plugin
**File:** `src/synapse/plugin_manager.py:575`
**Module:** `src.synapse.plugin_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for add_plugin in SynapseGateway.js
- Consider adding CLI command for add_plugin if appropriate

### remove_plugin
**File:** `src/synapse/plugin_manager.py:633`
**Module:** `src.synapse.plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for remove_plugin
- Add Synapse interface control for remove_plugin in SynapseGateway.js
- Consider adding CLI command for remove_plugin if appropriate

### activate_plugin
**File:** `src/synapse/plugin_manager.py:685`
**Module:** `src.synapse.plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for activate_plugin
- Add Synapse interface control for activate_plugin in SynapseGateway.js
- Consider adding CLI command for activate_plugin if appropriate

### deactivate_plugin
**File:** `src/synapse/plugin_manager.py:721`
**Module:** `src.synapse.plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for deactivate_plugin
- Add Synapse interface control for deactivate_plugin in SynapseGateway.js
- Consider adding CLI command for deactivate_plugin if appropriate

### list_plugins
**File:** `src/synapse/plugin_manager.py:751`
**Module:** `src.synapse.plugin_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_plugins
- Add Synapse interface control for list_plugins in SynapseGateway.js
- Consider adding CLI command for list_plugins if appropriate

### create_sandbox
**File:** `src/synapse/sandbox.py:77`
**Module:** `src.synapse.sandbox`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_sandbox
- Add Synapse interface control for create_sandbox in SynapseGateway.js
- Consider adding CLI command for create_sandbox if appropriate

### execute_in_sandbox
**File:** `src/synapse/sandbox.py:119`
**Module:** `src.synapse.sandbox`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_in_sandbox
- Add Synapse interface control for execute_in_sandbox in SynapseGateway.js
- Add CLI command wrapper for execute_in_sandbox

### get_sandbox_status
**File:** `src/synapse/sandbox.py:262`
**Module:** `src.synapse.sandbox`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_sandbox_status
- Add Synapse interface control for get_sandbox_status in SynapseGateway.js
- Consider adding CLI command for get_sandbox_status if appropriate

### list_active_sandboxes
**File:** `src/synapse/sandbox.py:267`
**Module:** `src.synapse.sandbox`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_active_sandboxes
- Add Synapse interface control for list_active_sandboxes in SynapseGateway.js
- Consider adding CLI command for list_active_sandboxes if appropriate

### monitor_resources
**File:** `src/synapse/sandbox.py:323`
**Module:** `src.synapse.sandbox`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for monitor_resources in SynapseGateway.js
- Consider adding CLI command for monitor_resources if appropriate

### check_synapse_permission
**File:** `src/synapse/security_manager.py:518`
**Module:** `src.synapse.security_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for check_synapse_permission in SynapseGateway.js
- Consider adding CLI command for check_synapse_permission if appropriate

### get_security_summary
**File:** `src/synapse/security_manager.py:526`
**Module:** `src.synapse.security_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_security_summary in SynapseGateway.js
- Consider adding CLI command for get_security_summary if appropriate

### get_agent_permissions
**File:** `src/synapse/security_manager.py:531`
**Module:** `src.synapse.security_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_permissions
- Add Synapse interface control for get_agent_permissions in SynapseGateway.js
- Consider adding CLI command for get_agent_permissions if appropriate

### log_security_event
**File:** `src/synapse/security_manager.py:105`
**Module:** `src.synapse.security_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_security_event
- Add Synapse interface control for log_security_event in SynapseGateway.js
- Consider adding CLI command for log_security_event if appropriate

### check_rate_limit
**File:** `src/synapse/security_manager.py:174`
**Module:** `src.synapse.security_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_rate_limit
- Add Synapse interface control for check_rate_limit in SynapseGateway.js
- Consider adding CLI command for check_rate_limit if appropriate

### get_rate_limit_status
**File:** `src/synapse/security_manager.py:214`
**Module:** `src.synapse.security_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_rate_limit_status in SynapseGateway.js
- Consider adding CLI command for get_rate_limit_status if appropriate

### check_permission
**File:** `src/synapse/security_manager.py:303`
**Module:** `src.synapse.security_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for check_permission in SynapseGateway.js
- Consider adding CLI command for check_permission if appropriate

### get_security_summary
**File:** `src/synapse/security_manager.py:430`
**Module:** `src.synapse.security_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_security_summary in SynapseGateway.js
- Consider adding CLI command for get_security_summary if appropriate

### get_agent_permissions
**File:** `src/synapse/security_manager.py:498`
**Module:** `src.synapse.security_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_permissions
- Add Synapse interface control for get_agent_permissions in SynapseGateway.js
- Consider adding CLI command for get_agent_permissions if appropriate

### get_rate_limit_status_for_agent
**File:** `src/synapse/security_manager.py:503`
**Module:** `src.synapse.security_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_rate_limit_status_for_agent in SynapseGateway.js
- Consider adding CLI command for get_rate_limit_status_for_agent if appropriate

### clear_security_events
**File:** `src/synapse/security_manager.py:508`
**Module:** `src.synapse.security_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for clear_security_events
- Add Synapse interface control for clear_security_events in SynapseGateway.js
- Consider adding CLI command for clear_security_events if appropriate

### register_default_hooks
**File:** `src/synapse/security_monitor.py:396`
**Module:** `src.synapse.security_monitor`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for register_default_hooks
- Add Synapse interface control for register_default_hooks in SynapseGateway.js
- Consider adding CLI command for register_default_hooks if appropriate

### check_webhook_request
**File:** `src/synapse/security_monitor.py:410`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_webhook_request
- Add Synapse interface control for check_webhook_request in SynapseGateway.js
- Consider adding CLI command for check_webhook_request if appropriate

### check_api_call
**File:** `src/synapse/security_monitor.py:420`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_api_call
- Add UI button/form calling check_api_call in appropriate React component
- Consider adding CLI command for check_api_call if appropriate

### check_browser_preview
**File:** `src/synapse/security_monitor.py:430`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_browser_preview
- Add Synapse interface control for check_browser_preview in SynapseGateway.js
- Consider adding CLI command for check_browser_preview if appropriate

### check_credential_access
**File:** `src/synapse/security_monitor.py:440`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_credential_access
- Add Synapse interface control for check_credential_access in SynapseGateway.js
- Consider adding CLI command for check_credential_access if appropriate

### check_credential_injection
**File:** `src/synapse/security_monitor.py:447`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_credential_injection
- Add Synapse interface control for check_credential_injection in SynapseGateway.js
- Consider adding CLI command for check_credential_injection if appropriate

### get_security_status
**File:** `src/synapse/security_monitor.py:454`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_security_status
- Add Synapse interface control for get_security_status in SynapseGateway.js
- Consider adding CLI command for get_security_status if appropriate

### check_rate_limit
**File:** `src/synapse/security_monitor.py:92`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_rate_limit
- Add Synapse interface control for check_rate_limit in SynapseGateway.js
- Consider adding CLI command for check_rate_limit if appropriate

### get_rate_limit_status
**File:** `src/synapse/security_monitor.py:113`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_rate_limit_status in SynapseGateway.js
- Consider adding CLI command for get_rate_limit_status if appropriate

### check_permission
**File:** `src/synapse/security_monitor.py:146`
**Module:** `src.synapse.security_monitor`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for check_permission in SynapseGateway.js
- Consider adding CLI command for check_permission if appropriate

### request_approval
**File:** `src/synapse/security_monitor.py:169`
**Module:** `src.synapse.security_monitor`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for request_approval
- Add Synapse interface control for request_approval in SynapseGateway.js
- Consider adding CLI command for request_approval if appropriate

### approve_request
**File:** `src/synapse/security_monitor.py:181`
**Module:** `src.synapse.security_monitor`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for approve_request
- Add Synapse interface control for approve_request in SynapseGateway.js
- Consider adding CLI command for approve_request if appropriate

### deny_request
**File:** `src/synapse/security_monitor.py:191`
**Module:** `src.synapse.security_monitor`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for deny_request
- Add Synapse interface control for deny_request in SynapseGateway.js
- Consider adding CLI command for deny_request if appropriate

### register_security_hook
**File:** `src/synapse/security_monitor.py:225`
**Module:** `src.synapse.security_monitor`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for register_security_hook
- Add Synapse interface control for register_security_hook in SynapseGateway.js
- Consider adding CLI command for register_security_hook if appropriate

### log_security_event
**File:** `src/synapse/security_monitor.py:230`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_security_event
- Add Synapse interface control for log_security_event in SynapseGateway.js
- Consider adding CLI command for log_security_event if appropriate

### check_and_log_request
**File:** `src/synapse/security_monitor.py:290`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_and_log_request
- Add Synapse interface control for check_and_log_request in SynapseGateway.js
- Consider adding CLI command for check_and_log_request if appropriate

### get_security_status
**File:** `src/synapse/security_monitor.py:331`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_security_status
- Add Synapse interface control for get_security_status in SynapseGateway.js
- Consider adding CLI command for get_security_status if appropriate

### stop
**File:** `src/synapse/security_monitor.py:353`
**Module:** `src.synapse.security_monitor`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for stop in SynapseGateway.js

### webhook_security_hook
**File:** `src/synapse/security_monitor.py:368`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for webhook_security_hook
- Add Synapse interface control for webhook_security_hook in SynapseGateway.js
- Consider adding CLI command for webhook_security_hook if appropriate

### credential_security_hook
**File:** `src/synapse/security_monitor.py:375`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for credential_security_hook
- Add Synapse interface control for credential_security_hook in SynapseGateway.js
- Consider adding CLI command for credential_security_hook if appropriate

### rate_limit_hook
**File:** `src/synapse/security_monitor.py:383`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for rate_limit_hook
- Add Synapse interface control for rate_limit_hook in SynapseGateway.js
- Consider adding CLI command for rate_limit_hook if appropriate

### permission_hook
**File:** `src/synapse/security_monitor.py:389`
**Module:** `src.synapse.security_monitor`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for permission_hook
- Add Synapse interface control for permission_hook in SynapseGateway.js
- Consider adding CLI command for permission_hook if appropriate

### create_security_dashboard
**File:** `src/synapse/security_ui.py:599`
**Module:** `src.synapse.security_ui`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_security_dashboard
- Add Synapse interface control for create_security_dashboard in SynapseGateway.js
- Consider adding CLI command for create_security_dashboard if appropriate

### show
**File:** `src/synapse/security_ui.py:453`
**Module:** `src.synapse.security_ui`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for show in SynapseGateway.js

### show
**File:** `src/synapse/security_ui.py:524`
**Module:** `src.synapse.security_ui`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for show in SynapseGateway.js

### monitor_synapse_operation
**File:** `src/synapse/sentry_integration.py:302`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for monitor_synapse_operation
- Add Synapse interface control for monitor_synapse_operation in SynapseGateway.js
- Consider adding CLI command for monitor_synapse_operation if appropriate

### get_sentry_monitor
**File:** `src/synapse/sentry_integration.py:379`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_sentry_monitor
- Add Synapse interface control for get_sentry_monitor in SynapseGateway.js
- Consider adding CLI command for get_sentry_monitor if appropriate

### register_module_for_monitoring
**File:** `src/synapse/sentry_integration.py:384`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for register_module_for_monitoring
- Add Synapse interface control for register_module_for_monitoring in SynapseGateway.js
- Consider adding CLI command for register_module_for_monitoring if appropriate

### monitor_outbound_request
**File:** `src/synapse/sentry_integration.py:389`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for monitor_outbound_request in SynapseGateway.js
- Consider adding CLI command for monitor_outbound_request if appropriate

### monitor_agent_interaction
**File:** `src/synapse/sentry_integration.py:399`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for monitor_agent_interaction in SynapseGateway.js
- Consider adding CLI command for monitor_agent_interaction if appropriate

### monitor_browser_preview
**File:** `src/synapse/sentry_integration.py:408`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for monitor_browser_preview in SynapseGateway.js
- Consider adding CLI command for monitor_browser_preview if appropriate

### monitor_webhook_config
**File:** `src/synapse/sentry_integration.py:417`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for monitor_webhook_config in SynapseGateway.js
- Consider adding CLI command for monitor_webhook_config if appropriate

### monitor_credential_access
**File:** `src/synapse/sentry_integration.py:426`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for monitor_credential_access in SynapseGateway.js
- Consider adding CLI command for monitor_credential_access if appropriate

### register_module
**File:** `src/synapse/sentry_integration.py:35`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for register_module in SynapseGateway.js
- Consider adding CLI command for register_module if appropriate

### add_alert_callback
**File:** `src/synapse/sentry_integration.py:40`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for add_alert_callback in SynapseGateway.js
- Consider adding CLI command for add_alert_callback if appropriate

### monitor_outbound_request
**File:** `src/synapse/sentry_integration.py:44`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for monitor_outbound_request in SynapseGateway.js
- Consider adding CLI command for monitor_outbound_request if appropriate

### monitor_agent_interaction
**File:** `src/synapse/sentry_integration.py:98`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for monitor_agent_interaction in SynapseGateway.js
- Consider adding CLI command for monitor_agent_interaction if appropriate

### monitor_browser_preview
**File:** `src/synapse/sentry_integration.py:131`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for monitor_browser_preview in SynapseGateway.js
- Consider adding CLI command for monitor_browser_preview if appropriate

### monitor_webhook_config
**File:** `src/synapse/sentry_integration.py:168`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for monitor_webhook_config in SynapseGateway.js
- Consider adding CLI command for monitor_webhook_config if appropriate

### monitor_credential_access
**File:** `src/synapse/sentry_integration.py:206`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for monitor_credential_access in SynapseGateway.js
- Consider adding CLI command for monitor_credential_access if appropriate

### get_monitoring_summary
**File:** `src/synapse/sentry_integration.py:291`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_monitoring_summary
- Add Synapse interface control for get_monitoring_summary in SynapseGateway.js
- Consider adding CLI command for get_monitoring_summary if appropriate

### decorator
**File:** `src/synapse/sentry_integration.py:305`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** test, ui_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for decorator
- Add Synapse interface control for decorator in SynapseGateway.js

### async_wrapper
**File:** `src/synapse/sentry_integration.py:307`
**Module:** `src.synapse.sentry_integration`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for async_wrapper
- Add Synapse interface control for async_wrapper in SynapseGateway.js
- Consider adding CLI command for async_wrapper if appropriate

### sync_wrapper
**File:** `src/synapse/sentry_integration.py:337`
**Module:** `src.synapse.sentry_integration`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for sync_wrapper
- Add Synapse interface control for sync_wrapper in SynapseGateway.js
- Consider adding CLI command for sync_wrapper if appropriate

### register_agent_process
**File:** `src/synapse/sentry_siem.py:136`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for register_agent_process
- Add Synapse interface control for register_agent_process in SynapseGateway.js
- Add CLI command wrapper for register_agent_process

### assess_process_risk
**File:** `src/synapse/sentry_siem.py:227`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for assess_process_risk
- Add Synapse interface control for assess_process_risk in SynapseGateway.js
- Add CLI command wrapper for assess_process_risk

### get_process_report
**File:** `src/synapse/sentry_siem.py:249`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_process_report
- Add Synapse interface control for get_process_report in SynapseGateway.js
- Add CLI command wrapper for get_process_report

### analyze_connection
**File:** `src/synapse/sentry_siem.py:282`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for analyze_connection
- Add Synapse interface control for analyze_connection in SynapseGateway.js
- Consider adding CLI command for analyze_connection if appropriate

### detect_anomaly
**File:** `src/synapse/sentry_siem.py:328`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for detect_anomaly
- Add Synapse interface control for detect_anomaly in SynapseGateway.js
- Consider adding CLI command for detect_anomaly if appropriate

### update_baseline
**File:** `src/synapse/sentry_siem.py:345`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_baseline
- Add Synapse interface control for update_baseline in SynapseGateway.js
- Consider adding CLI command for update_baseline if appropriate

### get_network_report
**File:** `src/synapse/sentry_siem.py:360`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_network_report
- Add Synapse interface control for get_network_report in SynapseGateway.js
- Consider adding CLI command for get_network_report if appropriate

### establish_baseline
**File:** `src/synapse/sentry_siem.py:388`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for establish_baseline
- Add Synapse interface control for establish_baseline in SynapseGateway.js
- Consider adding CLI command for establish_baseline if appropriate

### check_behavioral_anomaly
**File:** `src/synapse/sentry_siem.py:420`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_behavioral_anomaly
- Add Synapse interface control for check_behavioral_anomaly in SynapseGateway.js
- Consider adding CLI command for check_behavioral_anomaly if appropriate

### get_behavioral_report
**File:** `src/synapse/sentry_siem.py:465`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_behavioral_report
- Add Synapse interface control for get_behavioral_report in SynapseGateway.js
- Consider adding CLI command for get_behavioral_report if appropriate

### respond_to_threat
**File:** `src/synapse/sentry_siem.py:500`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for respond_to_threat
- Add Synapse interface control for respond_to_threat in SynapseGateway.js
- Consider adding CLI command for respond_to_threat if appropriate

### is_agent_quarantined
**File:** `src/synapse/sentry_siem.py:570`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for is_agent_quarantined in SynapseGateway.js
- Consider adding CLI command for is_agent_quarantined if appropriate

### release_quarantine
**File:** `src/synapse/sentry_siem.py:574`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for release_quarantine
- Add Synapse interface control for release_quarantine in SynapseGateway.js
- Consider adding CLI command for release_quarantine if appropriate

### monitor_agent_transaction
**File:** `src/synapse/sentry_siem.py:610`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for monitor_agent_transaction in SynapseGateway.js
- Consider adding CLI command for monitor_agent_transaction if appropriate

### get_security_report
**File:** `src/synapse/sentry_siem.py:738`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_security_report in SynapseGateway.js
- Consider adding CLI command for get_security_report if appropriate

### register_agent_process
**File:** `src/synapse/sentry_siem.py:765`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for register_agent_process
- Add Synapse interface control for register_agent_process in SynapseGateway.js
- Add CLI command wrapper for register_agent_process

### is_agent_quarantined
**File:** `src/synapse/sentry_siem.py:769`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for is_agent_quarantined in SynapseGateway.js
- Consider adding CLI command for is_agent_quarantined if appropriate

### release_quarantine
**File:** `src/synapse/sentry_siem.py:773`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for release_quarantine
- Add Synapse interface control for release_quarantine in SynapseGateway.js
- Consider adding CLI command for release_quarantine if appropriate

### shutdown
**File:** `src/synapse/sentry_siem.py:777`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for shutdown in SynapseGateway.js
- Consider adding CLI command for shutdown if appropriate

### name
**File:** `src/synapse/sentry_siem.py:23`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for name in SynapseGateway.js

### cmdline
**File:** `src/synapse/sentry_siem.py:24`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for cmdline
- Add Synapse interface control for cmdline in SynapseGateway.js
- Consider adding CLI command for cmdline if appropriate

### cpu_percent
**File:** `src/synapse/sentry_siem.py:25`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for cpu_percent
- Add Synapse interface control for cpu_percent in SynapseGateway.js
- Consider adding CLI command for cpu_percent if appropriate

### memory_percent
**File:** `src/synapse/sentry_siem.py:26`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for memory_percent
- Add Synapse interface control for memory_percent in SynapseGateway.js
- Consider adding CLI command for memory_percent if appropriate

### connections
**File:** `src/synapse/sentry_siem.py:27`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for connections in SynapseGateway.js
- Consider adding CLI command for connections if appropriate

### create_time
**File:** `src/synapse/sentry_siem.py:28`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_time
- Add Synapse interface control for create_time in SynapseGateway.js
- Consider adding CLI command for create_time if appropriate

### ppid
**File:** `src/synapse/sentry_siem.py:29`
**Module:** `src.synapse.sentry_siem`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for ppid
- Add Synapse interface control for ppid in SynapseGateway.js
- Consider adding CLI command for ppid if appropriate

### register_plugin
**File:** `src/synapse/synapse.py:111`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for register_plugin in SynapseGateway.js
- Consider adding CLI command for register_plugin if appropriate

### approve_plugin
**File:** `src/synapse/synapse.py:124`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for approve_plugin in SynapseGateway.js
- Consider adding CLI command for approve_plugin if appropriate

### revoke_plugin
**File:** `src/synapse/synapse.py:138`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for revoke_plugin
- Add Synapse interface control for revoke_plugin in SynapseGateway.js
- Consider adding CLI command for revoke_plugin if appropriate

### execute_plugin
**File:** `src/synapse/synapse.py:152`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for execute_plugin in SynapseGateway.js
- Add CLI command wrapper for execute_plugin

### get_plugin_status
**File:** `src/synapse/synapse.py:260`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_plugin_status
- Add Synapse interface control for get_plugin_status in SynapseGateway.js
- Consider adding CLI command for get_plugin_status if appropriate

### list_plugins
**File:** `src/synapse/synapse.py:264`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_plugins
- Add Synapse interface control for list_plugins in SynapseGateway.js
- Consider adding CLI command for list_plugins if appropriate

### get_plugin_manifest
**File:** `src/synapse/synapse.py:268`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_plugin_manifest
- Add Synapse interface control for get_plugin_manifest in SynapseGateway.js
- Consider adding CLI command for get_plugin_manifest if appropriate

### request_permissions
**File:** `src/synapse/synapse.py:274`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for request_permissions
- Add Synapse interface control for request_permissions in SynapseGateway.js
- Consider adding CLI command for request_permissions if appropriate

### approve_permissions
**File:** `src/synapse/synapse.py:288`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for approve_permissions
- Add Synapse interface control for approve_permissions in SynapseGateway.js
- Consider adding CLI command for approve_permissions if appropriate

### deny_permissions
**File:** `src/synapse/synapse.py:302`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for deny_permissions
- Add Synapse interface control for deny_permissions in SynapseGateway.js
- Consider adding CLI command for deny_permissions if appropriate

### check_permission
**File:** `src/synapse/synapse.py:316`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for check_permission in SynapseGateway.js
- Consider adding CLI command for check_permission if appropriate

### get_pending_permission_requests
**File:** `src/synapse/synapse.py:329`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_pending_permission_requests
- Add Synapse interface control for get_pending_permission_requests in SynapseGateway.js
- Consider adding CLI command for get_pending_permission_requests if appropriate

### request_connection
**File:** `src/synapse/synapse.py:335`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for request_connection in SynapseGateway.js
- Consider adding CLI command for request_connection if appropriate

### approve_connection
**File:** `src/synapse/synapse.py:374`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for approve_connection in SynapseGateway.js
- Consider adding CLI command for approve_connection if appropriate

### close_connection
**File:** `src/synapse/synapse.py:419`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for close_connection in SynapseGateway.js
- Consider adding CLI command for close_connection if appropriate

### run_benchmark
**File:** `src/synapse/synapse.py:457`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for run_benchmark
- Add Synapse interface control for run_benchmark in SynapseGateway.js
- Consider adding CLI command for run_benchmark if appropriate

### get_benchmark_summary
**File:** `src/synapse/synapse.py:473`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_benchmark_summary
- Add Synapse interface control for get_benchmark_summary in SynapseGateway.js
- Consider adding CLI command for get_benchmark_summary if appropriate

### get_performance_tier
**File:** `src/synapse/synapse.py:478`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_performance_tier in SynapseGateway.js
- Consider adding CLI command for get_performance_tier if appropriate

### get_risk_score
**File:** `src/synapse/synapse.py:483`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_risk_score
- Add Synapse interface control for get_risk_score in SynapseGateway.js
- Consider adding CLI command for get_risk_score if appropriate

### get_traffic_logs
**File:** `src/synapse/synapse.py:489`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_traffic_logs
- Add Synapse interface control for get_traffic_logs in SynapseGateway.js
- Consider adding CLI command for get_traffic_logs if appropriate

### get_traffic_summary
**File:** `src/synapse/synapse.py:494`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_traffic_summary
- Add Synapse interface control for get_traffic_summary in SynapseGateway.js
- Consider adding CLI command for get_traffic_summary if appropriate

### export_traffic_logs
**File:** `src/synapse/synapse.py:499`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_traffic_logs
- Add Synapse interface control for export_traffic_logs in SynapseGateway.js
- Consider adding CLI command for export_traffic_logs if appropriate

### get_traffic_statistics
**File:** `src/synapse/synapse.py:503`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_traffic_statistics
- Add Synapse interface control for get_traffic_statistics in SynapseGateway.js
- Consider adding CLI command for get_traffic_statistics if appropriate

### get_sandbox_status
**File:** `src/synapse/synapse.py:509`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_sandbox_status
- Add Synapse interface control for get_sandbox_status in SynapseGateway.js
- Consider adding CLI command for get_sandbox_status if appropriate

### list_active_sandboxes
**File:** `src/synapse/synapse.py:513`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_active_sandboxes
- Add Synapse interface control for list_active_sandboxes in SynapseGateway.js
- Consider adding CLI command for list_active_sandboxes if appropriate

### get_system_status
**File:** `src/synapse/synapse.py:523`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_system_status in SynapseGateway.js
- Consider adding CLI command for get_system_status if appropriate

### export_system_data
**File:** `src/synapse/synapse.py:548`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_system_data
- Add Synapse interface control for export_system_data in SynapseGateway.js
- Consider adding CLI command for export_system_data if appropriate

### get_traffic_metrics
**File:** `src/synapse/synapse.py:581`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_traffic_metrics in SynapseGateway.js
- Consider adding CLI command for get_traffic_metrics if appropriate

### get_security_report
**File:** `src/synapse/synapse.py:585`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_security_report in SynapseGateway.js
- Consider adding CLI command for get_security_report if appropriate

### update_user_bandwidth
**File:** `src/synapse/synapse.py:589`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for update_user_bandwidth in SynapseGateway.js
- Consider adding CLI command for update_user_bandwidth if appropriate

### register_agent_process
**File:** `src/synapse/synapse.py:593`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for register_agent_process
- Add Synapse interface control for register_agent_process in SynapseGateway.js
- Add CLI command wrapper for register_agent_process

### is_agent_quarantined
**File:** `src/synapse/synapse.py:597`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for is_agent_quarantined in SynapseGateway.js
- Consider adding CLI command for is_agent_quarantined if appropriate

### release_agent_quarantine
**File:** `src/synapse/synapse.py:601`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for release_agent_quarantine
- Add Synapse interface control for release_agent_quarantine in SynapseGateway.js
- Consider adding CLI command for release_agent_quarantine if appropriate

### launch_local_resource
**File:** `src/synapse/synapse.py:607`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for launch_local_resource
- Add Synapse interface control for launch_local_resource in SynapseGateway.js
- Consider adding CLI command for launch_local_resource if appropriate

### get_connections
**File:** `src/synapse/synapse.py:746`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_connections
- Add Synapse interface control for get_connections in SynapseGateway.js
- Consider adding CLI command for get_connections if appropriate

### get_webhooks
**File:** `src/synapse/synapse.py:787`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_webhooks
- Add Synapse interface control for get_webhooks in SynapseGateway.js
- Consider adding CLI command for get_webhooks if appropriate

### create_webhook
**File:** `src/synapse/synapse.py:810`
**Module:** `src.synapse.synapse`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_webhook
- Add Synapse interface control for create_webhook in SynapseGateway.js
- Consider adding CLI command for create_webhook if appropriate

### log_traffic
**File:** `src/synapse/traffic_logger.py:119`
**Module:** `src.synapse.traffic_logger`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_traffic
- Add Synapse interface control for log_traffic in SynapseGateway.js
- Consider adding CLI command for log_traffic if appropriate

### get_traffic_logs
**File:** `src/synapse/traffic_logger.py:196`
**Module:** `src.synapse.traffic_logger`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_traffic_logs
- Add Synapse interface control for get_traffic_logs in SynapseGateway.js
- Consider adding CLI command for get_traffic_logs if appropriate

### get_traffic_summary
**File:** `src/synapse/traffic_logger.py:252`
**Module:** `src.synapse.traffic_logger`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_traffic_summary
- Add Synapse interface control for get_traffic_summary in SynapseGateway.js
- Consider adding CLI command for get_traffic_summary if appropriate

### get_connection_logs
**File:** `src/synapse/traffic_logger.py:339`
**Module:** `src.synapse.traffic_logger`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_connection_logs
- Add Synapse interface control for get_connection_logs in SynapseGateway.js
- Consider adding CLI command for get_connection_logs if appropriate

### export_traffic_logs
**File:** `src/synapse/traffic_logger.py:348`
**Module:** `src.synapse.traffic_logger`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_traffic_logs
- Add Synapse interface control for export_traffic_logs in SynapseGateway.js
- Consider adding CLI command for export_traffic_logs if appropriate

### get_traffic_statistics
**File:** `src/synapse/traffic_logger.py:384`
**Module:** `src.synapse.traffic_logger`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_traffic_statistics
- Add Synapse interface control for get_traffic_statistics in SynapseGateway.js
- Consider adding CLI command for get_traffic_statistics if appropriate

### consume
**File:** `src/synapse/traffic_manager.py:46`
**Module:** `src.synapse.traffic_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for consume
- Add Synapse interface control for consume in SynapseGateway.js
- Consider adding CLI command for consume if appropriate

### update
**File:** `src/synapse/traffic_manager.py:85`
**Module:** `src.synapse.traffic_manager`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for update in SynapseGateway.js

### get_user_budget
**File:** `src/synapse/traffic_manager.py:105`
**Module:** `src.synapse.traffic_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_user_budget
- Add Synapse interface control for get_user_budget in SynapseGateway.js
- Consider adding CLI command for get_user_budget if appropriate

### update_user_budget
**File:** `src/synapse/traffic_manager.py:120`
**Module:** `src.synapse.traffic_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_user_budget
- Add Synapse interface control for update_user_budget in SynapseGateway.js
- Consider adding CLI command for update_user_budget if appropriate

### record_request
**File:** `src/synapse/traffic_manager.py:141`
**Module:** `src.synapse.traffic_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for record_request
- Add Synapse interface control for record_request in SynapseGateway.js
- Consider adding CLI command for record_request if appropriate

### detect_anomaly
**File:** `src/synapse/traffic_manager.py:156`
**Module:** `src.synapse.traffic_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for detect_anomaly
- Add Synapse interface control for detect_anomaly in SynapseGateway.js
- Consider adding CLI command for detect_anomaly if appropriate

### get_security_report
**File:** `src/synapse/traffic_manager.py:168`
**Module:** `src.synapse.traffic_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_security_report in SynapseGateway.js
- Consider adding CLI command for get_security_report if appropriate

### get_agent_priority
**File:** `src/synapse/traffic_manager.py:246`
**Module:** `src.synapse.traffic_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_agent_priority
- Add Synapse interface control for get_agent_priority in SynapseGateway.js
- Consider adding CLI command for get_agent_priority if appropriate

### submit_request
**File:** `src/synapse/traffic_manager.py:259`
**Module:** `src.synapse.traffic_manager`
**Type:** async_function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for submit_request in SynapseGateway.js
- Consider adding CLI command for submit_request if appropriate

### get_system_metrics
**File:** `src/synapse/traffic_manager.py:461`
**Module:** `src.synapse.traffic_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_system_metrics in SynapseGateway.js
- Consider adding CLI command for get_system_metrics if appropriate

### get_security_report
**File:** `src/synapse/traffic_manager.py:486`
**Module:** `src.synapse.traffic_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for get_security_report in SynapseGateway.js
- Consider adding CLI command for get_security_report if appropriate

### update_user_budget
**File:** `src/synapse/traffic_manager.py:490`
**Module:** `src.synapse.traffic_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_user_budget
- Add Synapse interface control for update_user_budget in SynapseGateway.js
- Consider adding CLI command for update_user_budget if appropriate

### shutdown
**File:** `src/synapse/traffic_manager.py:495`
**Module:** `src.synapse.traffic_manager`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for shutdown in SynapseGateway.js
- Consider adding CLI command for shutdown if appropriate

### create_webhook
**File:** `src/synapse/webhook_manager.py:452`
**Module:** `src.synapse.webhook_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_webhook
- Add Synapse interface control for create_webhook in SynapseGateway.js
- Consider adding CLI command for create_webhook if appropriate

### execute_webhook
**File:** `src/synapse/webhook_manager.py:458`
**Module:** `src.synapse.webhook_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_webhook
- Add Synapse interface control for execute_webhook in SynapseGateway.js
- Add CLI command wrapper for execute_webhook

### list_webhooks
**File:** `src/synapse/webhook_manager.py:469`
**Module:** `src.synapse.webhook_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_webhooks
- Add Synapse interface control for list_webhooks in SynapseGateway.js
- Consider adding CLI command for list_webhooks if appropriate

### get_webhook
**File:** `src/synapse/webhook_manager.py:474`
**Module:** `src.synapse.webhook_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_webhook
- Add Synapse interface control for get_webhook in SynapseGateway.js
- Consider adding CLI command for get_webhook if appropriate

### create_webhook
**File:** `src/synapse/webhook_manager.py:122`
**Module:** `src.synapse.webhook_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_webhook
- Add Synapse interface control for create_webhook in SynapseGateway.js
- Consider adding CLI command for create_webhook if appropriate

### update_webhook
**File:** `src/synapse/webhook_manager.py:145`
**Module:** `src.synapse.webhook_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for update_webhook
- Add Synapse interface control for update_webhook in SynapseGateway.js
- Consider adding CLI command for update_webhook if appropriate

### delete_webhook
**File:** `src/synapse/webhook_manager.py:169`
**Module:** `src.synapse.webhook_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for delete_webhook
- Add Synapse interface control for delete_webhook in SynapseGateway.js
- Consider adding CLI command for delete_webhook if appropriate

### get_webhook
**File:** `src/synapse/webhook_manager.py:179`
**Module:** `src.synapse.webhook_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_webhook
- Add Synapse interface control for get_webhook in SynapseGateway.js
- Consider adding CLI command for get_webhook if appropriate

### list_webhooks
**File:** `src/synapse/webhook_manager.py:183`
**Module:** `src.synapse.webhook_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_webhooks
- Add Synapse interface control for list_webhooks in SynapseGateway.js
- Consider adding CLI command for list_webhooks if appropriate

### execute_webhook
**File:** `src/synapse/webhook_manager.py:187`
**Module:** `src.synapse.webhook_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_webhook
- Add Synapse interface control for execute_webhook in SynapseGateway.js
- Add CLI command wrapper for execute_webhook

### validate_webhook_config
**File:** `src/synapse/webhook_manager.py:340`
**Module:** `src.synapse.webhook_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_webhook_config
- Add Synapse interface control for validate_webhook_config in SynapseGateway.js
- Consider adding CLI command for validate_webhook_config if appropriate

### list_webhooks_cli
**File:** `src/synapse/webhook_manager.py:413`
**Module:** `src.synapse.webhook_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_webhooks_cli
- Add Synapse interface control for list_webhooks_cli in SynapseGateway.js
- Consider adding CLI command for list_webhooks_cli if appropriate

### create_webhook_cli
**File:** `src/synapse/webhook_manager.py:434`
**Module:** `src.synapse.webhook_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_webhook_cli
- Add Synapse interface control for create_webhook_cli in SynapseGateway.js
- Consider adding CLI command for create_webhook_cli if appropriate

### get_mcp_manager
**File:** `src/synapse/api/mcp_endpoints.py:49`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_mcp_manager
- Add Synapse interface control for get_mcp_manager in SynapseGateway.js
- Consider adding CLI command for get_mcp_manager if appropriate

### list_mcp_servers
**File:** `src/synapse/api/mcp_endpoints.py:56`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_mcp_servers
- Add Synapse interface control for list_mcp_servers in SynapseGateway.js
- Consider adding CLI command for list_mcp_servers if appropriate

### get_mcp_server
**File:** `src/synapse/api/mcp_endpoints.py:86`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_mcp_server
- Add Synapse interface control for get_mcp_server in SynapseGateway.js
- Consider adding CLI command for get_mcp_server if appropriate

### start_mcp_server
**File:** `src/synapse/api/mcp_endpoints.py:119`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_mcp_server
- Add Synapse interface control for start_mcp_server in SynapseGateway.js
- Consider adding CLI command for start_mcp_server if appropriate

### stop_mcp_server
**File:** `src/synapse/api/mcp_endpoints.py:140`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for stop_mcp_server
- Add Synapse interface control for stop_mcp_server in SynapseGateway.js
- Consider adding CLI command for stop_mcp_server if appropriate

### get_mcp_server_tools
**File:** `src/synapse/api/mcp_endpoints.py:161`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_mcp_server_tools
- Add Synapse interface control for get_mcp_server_tools in SynapseGateway.js
- Consider adding CLI command for get_mcp_server_tools if appropriate

### execute_mcp_tool
**File:** `src/synapse/api/mcp_endpoints.py:188`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_mcp_tool
- Add Synapse interface control for execute_mcp_tool in SynapseGateway.js
- Add CLI command wrapper for execute_mcp_tool

### get_mcp_server_health
**File:** `src/synapse/api/mcp_endpoints.py:216`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_mcp_server_health
- Add Synapse interface control for get_mcp_server_health in SynapseGateway.js
- Consider adding CLI command for get_mcp_server_health if appropriate

### get_all_mcp_health
**File:** `src/synapse/api/mcp_endpoints.py:246`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_all_mcp_health
- Add Synapse interface control for get_all_mcp_health in SynapseGateway.js
- Consider adding CLI command for get_all_mcp_health if appropriate

### send_gmail
**File:** `src/synapse/api/mcp_endpoints.py:271`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for send_gmail
- Add Synapse interface control for send_gmail in SynapseGateway.js
- Consider adding CLI command for send_gmail if appropriate

### list_gmail_emails
**File:** `src/synapse/api/mcp_endpoints.py:304`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_gmail_emails
- Add Synapse interface control for list_gmail_emails in SynapseGateway.js
- Consider adding CLI command for list_gmail_emails if appropriate

### list_calendar_events
**File:** `src/synapse/api/mcp_endpoints.py:333`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_calendar_events
- Add Synapse interface control for list_calendar_events in SynapseGateway.js
- Consider adding CLI command for list_calendar_events if appropriate

### create_calendar_event
**File:** `src/synapse/api/mcp_endpoints.py:366`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_calendar_event
- Add Synapse interface control for create_calendar_event in SynapseGateway.js
- Consider adding CLI command for create_calendar_event if appropriate

### create_agent
**File:** `src/synapse/plugins/google-ai/plugin.py:361`
**Module:** `src.synapse.plugins.google-ai.plugin`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Synapse interface control for create_agent in SynapseGateway.js
- Consider adding CLI command for create_agent if appropriate

### execute
**File:** `src/synapse/plugins/google-ai/plugin.py:40`
**Module:** `src.synapse.plugins.google-ai.plugin`
**Type:** function
**Missing:** ui_invocation

**Recommendations:**
- Add Synapse interface control for execute in SynapseGateway.js

### get_recovery_status
**File:** `src/utils/automatic_recovery_orchestrator.py:672`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_recovery_status
- Consider adding UI control for get_recovery_status if user-facing
- Consider adding CLI command for get_recovery_status if appropriate

### execute_recovery
**File:** `src/utils/automatic_recovery_orchestrator.py:278`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_recovery
- Consider adding UI control for execute_recovery if user-facing
- Add CLI command wrapper for execute_recovery

### get_orchestrator_status
**File:** `src/utils/automatic_recovery_orchestrator.py:597`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_orchestrator_status
- Consider adding UI control for get_orchestrator_status if user-facing
- Consider adding CLI command for get_orchestrator_status if appropriate

### get_failure_rate
**File:** `src/utils/circuit_breaker.py:76`
**Module:** `src.utils.circuit_breaker`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_failure_rate
- Consider adding UI control for get_failure_rate if user-facing
- Consider adding CLI command for get_failure_rate if appropriate

### get_status
**File:** `src/utils/circuit_breaker.py:211`
**Module:** `src.utils.circuit_breaker`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### get_or_create
**File:** `src/utils/circuit_breaker.py:264`
**Module:** `src.utils.circuit_breaker`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_or_create if user-facing
- Consider adding CLI command for get_or_create if appropriate

### get_breaker
**File:** `src/utils/circuit_breaker.py:272`
**Module:** `src.utils.circuit_breaker`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_breaker
- Consider adding UI control for get_breaker if user-facing
- Consider adding CLI command for get_breaker if appropriate

### get_all_status
**File:** `src/utils/circuit_breaker.py:276`
**Module:** `src.utils.circuit_breaker`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_all_status
- Consider adding UI control for get_all_status if user-facing
- Consider adding CLI command for get_all_status if appropriate

### get_env
**File:** `src/utils/env_loader.py:288`
**Module:** `src.utils.env_loader`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_env
- Consider adding UI control for get_env if user-facing
- Consider adding CLI command for get_env if appropriate

### get_env_int
**File:** `src/utils/env_loader.py:292`
**Module:** `src.utils.env_loader`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_env_int
- Consider adding UI control for get_env_int if user-facing
- Consider adding CLI command for get_env_int if appropriate

### get_env_bool
**File:** `src/utils/env_loader.py:296`
**Module:** `src.utils.env_loader`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_env_bool
- Consider adding UI control for get_env_bool if user-facing
- Consider adding CLI command for get_env_bool if appropriate

### get_int
**File:** `src/utils/env_loader.py:125`
**Module:** `src.utils.env_loader`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_int if user-facing
- Consider adding CLI command for get_int if appropriate

### get_bool
**File:** `src/utils/env_loader.py:138`
**Module:** `src.utils.env_loader`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_bool
- Consider adding UI control for get_bool if user-facing
- Consider adding CLI command for get_bool if appropriate

### get_float
**File:** `src/utils/env_loader.py:147`
**Module:** `src.utils.env_loader`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_float
- Consider adding UI control for get_float if user-facing
- Consider adding CLI command for get_float if appropriate

### get_list
**File:** `src/utils/env_loader.py:160`
**Module:** `src.utils.env_loader`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_list
- Consider adding UI control for get_list if user-facing
- Consider adding CLI command for get_list if appropriate

### get_database_config
**File:** `src/utils/env_loader.py:195`
**Module:** `src.utils.env_loader`
**Type:** function
**Missing:** test, ui_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_database_config
- Consider adding UI control for get_database_config if user-facing

### get_api_keys
**File:** `src/utils/env_loader.py:226`
**Module:** `src.utils.env_loader`
**Type:** function
**Missing:** test, ui_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_api_keys
- Add UI button/form calling get_api_keys in appropriate React component

### get_security_config
**File:** `src/utils/env_loader.py:238`
**Module:** `src.utils.env_loader`
**Type:** function
**Missing:** test, ui_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_security_config
- Consider adding UI control for get_security_config if user-facing

### get_service_config
**File:** `src/utils/env_loader.py:249`
**Module:** `src.utils.env_loader`
**Type:** function
**Missing:** test, ui_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_service_config
- Consider adding UI control for get_service_config if user-facing

### create_optimized_schema
**File:** `src/utils/memory_optimizer.py:115`
**Module:** `src.utils.memory_optimizer`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_optimized_schema
- Consider adding UI control for create_optimized_schema if user-facing
- Consider adding CLI command for create_optimized_schema if appropriate

### get_cached_response
**File:** `src/utils/performance_optimizer.py:65`
**Module:** `src.utils.performance_optimizer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_cached_response
- Consider adding UI control for get_cached_response if user-facing
- Consider adding CLI command for get_cached_response if appropriate

### get_performance_metrics
**File:** `src/utils/performance_optimizer.py:363`
**Module:** `src.utils.performance_optimizer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_performance_metrics
- Consider adding UI control for get_performance_metrics if user-facing
- Consider adding CLI command for get_performance_metrics if appropriate

### get_recovery_status
**File:** `src/utils/service_recovery_manager.py:674`
**Module:** `src.utils.service_recovery_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_recovery_status
- Consider adding UI control for get_recovery_status if user-facing
- Consider adding CLI command for get_recovery_status if appropriate

### execute_recovery_action
**File:** `src/utils/service_recovery_manager.py:420`
**Module:** `src.utils.service_recovery_manager`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for execute_recovery_action
- Consider adding UI control for execute_recovery_action if user-facing
- Add CLI command wrapper for execute_recovery_action

### get_service_status
**File:** `src/utils/service_recovery_manager.py:611`
**Module:** `src.utils.service_recovery_manager`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for get_service_status
- Consider adding UI control for get_service_status if user-facing
- Consider adding CLI command for get_service_status if appropriate

### create_watchdog_service
**File:** `src/utils/service_watchdog.py:351`
**Module:** `src.utils.service_watchdog`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for create_watchdog_service
- Consider adding UI control for create_watchdog_service if user-facing
- Consider adding CLI command for create_watchdog_service if appropriate

### handle_service_failure
**File:** `src/utils/service_watchdog.py:211`
**Module:** `src.utils.service_watchdog`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for handle_service_failure
- Consider adding UI control for handle_service_failure if user-facing
- Consider adding CLI command for handle_service_failure if appropriate

### get_status
**File:** `src/utils/service_watchdog.py:257`
**Module:** `src.utils.service_watchdog`
**Type:** function
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for get_status if user-facing
- Consider adding CLI command for get_status if appropriate

### run_daemon
**File:** `src/utils/service_watchdog.py:333`
**Module:** `src.utils.service_watchdog`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for run_daemon
- Consider adding UI control for run_daemon if user-facing
- Consider adding CLI command for run_daemon if appropriate

### run_smoke_tests
**File:** `scripts/run_performance_tests.py:61`
**Module:** `scripts.run_performance_tests`
**Type:** async_function
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for run_smoke_tests
- Consider adding UI control for run_smoke_tests if user-facing

### run_load_tests
**File:** `scripts/run_performance_tests.py:112`
**Module:** `scripts.run_performance_tests`
**Type:** async_function
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for run_load_tests
- Consider adding UI control for run_load_tests if user-facing

### run_installer_tests
**File:** `scripts/run_performance_tests.py:214`
**Module:** `scripts.run_performance_tests`
**Type:** async_function
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for run_installer_tests
- Consider adding UI control for run_installer_tests if user-facing

### get_rotation_manager
**File:** `scripts/vault_rotation_cli.py:57`
**Module:** `scripts.vault_rotation_cli`
**Type:** function
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for get_rotation_manager
- Consider adding UI control for get_rotation_manager if user-facing

### run_verification
**File:** `scripts/verify_env.py:457`
**Module:** `scripts.verify_env`
**Type:** function
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for run_verification
- Consider adding UI control for run_verification if user-facing

### StartupSettings
**File:** `src/components/StartupSettings.tsx:17`
**Module:** `src.components.StartupSettings`
**Type:** react_component
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add React Testing Library test in tests/components/ for StartupSettings
- Ensure StartupSettings component is imported and used in parent components
- Consider adding CLI command for StartupSettings if appropriate

### Card
**File:** `src/components/ui/index.tsx:57`
**Module:** `src.components.ui.index`
**Type:** react_component
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add React Testing Library test in tests/components/ for Card
- Ensure Card component is imported and used in parent components
- Consider adding CLI command for Card if appropriate

### CardContent
**File:** `src/components/ui/index.tsx:67`
**Module:** `src.components.ui.index`
**Type:** react_component
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add React Testing Library test in tests/components/ for CardContent
- Ensure CardContent component is imported and used in parent components
- Consider adding CLI command for CardContent if appropriate

### Badge
**File:** `src/components/ui/index.tsx:129`
**Module:** `src.components.ui.index`
**Type:** react_component
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add React Testing Library test in tests/components/ for Badge
- Ensure Badge component is imported and used in parent components
- Consider adding CLI command for Badge if appropriate

### AlertTitle
**File:** `src/components/ui/index.tsx:157`
**Module:** `src.components.ui.index`
**Type:** react_component
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add React Testing Library test in tests/components/ for AlertTitle
- Ensure AlertTitle component is imported and used in parent components
- Consider adding CLI command for AlertTitle if appropriate

### AlertDescription
**File:** `src/components/ui/index.tsx:163`
**Module:** `src.components.ui.index`
**Type:** react_component
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add React Testing Library test in tests/components/ for AlertDescription
- Ensure AlertDescription component is imported and used in parent components
- Consider adding CLI command for AlertDescription if appropriate

### getSentryPersona
**File:** `src/personas/sentry/sentry.ts:660`
**Module:** `src.personas.sentry.sentry`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getSentryPersona
- Consider adding UI control for getSentryPersona if user-facing
- Consider adding CLI command for getSentryPersona if appropriate

### recordModelActivation
**File:** `src/core/SpriteEngine.js:30`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for recordModelActivation
- Add Core interface control for recordModelActivation in CoreInterface.js
- Add core management CLI command for recordModelActivation

### recordModelDeactivation
**File:** `src/core/SpriteEngine.js:61`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for recordModelDeactivation
- Add Core interface control for recordModelDeactivation in CoreInterface.js
- Add core management CLI command for recordModelDeactivation

### recordModelRequest
**File:** `src/core/SpriteEngine.js:80`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for recordModelRequest
- Add Core interface control for recordModelRequest in CoreInterface.js
- Add core management CLI command for recordModelRequest

### recordThermalEvent
**File:** `src/core/SpriteEngine.js:97`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for recordThermalEvent
- Add Core interface control for recordThermalEvent in CoreInterface.js
- Add core management CLI command for recordThermalEvent

### updateMemoryUsage
**File:** `src/core/SpriteEngine.js:123`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for updateMemoryUsage
- Add Core interface control for updateMemoryUsage in CoreInterface.js
- Add core management CLI command for updateMemoryUsage

### logSentryEvent
**File:** `src/core/SpriteEngine.js:138`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for logSentryEvent
- Add Core interface control for logSentryEvent in CoreInterface.js
- Add core management CLI command for logSentryEvent

### getPowerMetrics
**File:** `src/core/SpriteEngine.js:186`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getPowerMetrics
- Add Core interface control for getPowerMetrics in CoreInterface.js
- Add core management CLI command for getPowerMetrics

### getModelActivationSummary
**File:** `src/core/SpriteEngine.js:202`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getModelActivationSummary
- Add Core interface control for getModelActivationSummary in CoreInterface.js
- Add core management CLI command for getModelActivationSummary

### startThermalMonitoring
**File:** `src/core/SpriteEngine.js:248`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for startThermalMonitoring
- Add Core interface control for startThermalMonitoring in CoreInterface.js
- Add core management CLI command for startThermalMonitoring

### startMemoryMonitoring
**File:** `src/core/SpriteEngine.js:255`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for startMemoryMonitoring
- Add Core interface control for startMemoryMonitoring in CoreInterface.js
- Add core management CLI command for startMemoryMonitoring

### checkThermalStatus
**File:** `src/core/SpriteEngine.js:262`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for checkThermalStatus
- Add Core interface control for checkThermalStatus in CoreInterface.js
- Add core management CLI command for checkThermalStatus

### checkMemoryPressure
**File:** `src/core/SpriteEngine.js:303`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for checkMemoryPressure
- Add Core interface control for checkMemoryPressure in CoreInterface.js
- Add core management CLI command for checkMemoryPressure

### enforceMemoryBudget
**File:** `src/core/SpriteEngine.js:346`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for enforceMemoryBudget
- Add Core interface control for enforceMemoryBudget in CoreInterface.js
- Add core management CLI command for enforceMemoryBudget

### triggerEmergencyThermalShutdown
**File:** `src/core/SpriteEngine.js:363`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for triggerEmergencyThermalShutdown
- Add Core interface control for triggerEmergencyThermalShutdown in CoreInterface.js
- Add core management CLI command for triggerEmergencyThermalShutdown

### enableThermalThrottling
**File:** `src/core/SpriteEngine.js:384`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for enableThermalThrottling
- Add Core interface control for enableThermalThrottling in CoreInterface.js
- Add core management CLI command for enableThermalThrottling

### enablePowerSaveMode
**File:** `src/core/SpriteEngine.js:405`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for enablePowerSaveMode
- Add Core interface control for enablePowerSaveMode in CoreInterface.js
- Add core management CLI command for enablePowerSaveMode

### disableThermalThrottling
**File:** `src/core/SpriteEngine.js:417`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for disableThermalThrottling
- Add Core interface control for disableThermalThrottling in CoreInterface.js
- Add core management CLI command for disableThermalThrottling

### getSystemTemperature
**File:** `src/core/SpriteEngine.js:439`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getSystemTemperature
- Add Core interface control for getSystemTemperature in CoreInterface.js
- Add core management CLI command for getSystemTemperature

### getGPUTemperature
**File:** `src/core/SpriteEngine.js:444`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getGPUTemperature
- Add Core interface control for getGPUTemperature in CoreInterface.js
- Add core management CLI command for getGPUTemperature

### getMemoryUsage
**File:** `src/core/SpriteEngine.js:449`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getMemoryUsage
- Add Core interface control for getMemoryUsage in CoreInterface.js
- Add core management CLI command for getMemoryUsage

### canLoadModel
**File:** `src/core/SpriteEngine.js:463`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for canLoadModel
- Add Core interface control for canLoadModel in CoreInterface.js
- Add core management CLI command for canLoadModel

### addPowerEnforcementCallback
**File:** `src/core/SpriteEngine.js:493`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for addPowerEnforcementCallback
- Add Core interface control for addPowerEnforcementCallback in CoreInterface.js
- Add core management CLI command for addPowerEnforcementCallback

### updatePowerBudget
**File:** `src/core/SpriteEngine.js:497`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for updatePowerBudget
- Add Core interface control for updatePowerBudget in CoreInterface.js
- Add core management CLI command for updatePowerBudget

### getPowerStatus
**File:** `src/core/SpriteEngine.js:502`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getPowerStatus
- Add Core interface control for getPowerStatus in CoreInterface.js
- Add core management CLI command for getPowerStatus

### handleEmergencyShutdown
**File:** `src/core/SpriteEngine.js:674`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for handleEmergencyShutdown
- Add Core interface control for handleEmergencyShutdown in CoreInterface.js
- Add core management CLI command for handleEmergencyShutdown

### handleMemoryPressure
**File:** `src/core/SpriteEngine.js:688`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for handleMemoryPressure
- Add Core interface control for handleMemoryPressure in CoreInterface.js
- Add core management CLI command for handleMemoryPressure

### handleThermalThrottling
**File:** `src/core/SpriteEngine.js:703`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for handleThermalThrottling
- Add Core interface control for handleThermalThrottling in CoreInterface.js
- Add core management CLI command for handleThermalThrottling

### loadConfiguration
**File:** `src/core/SpriteEngine.js:715`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for loadConfiguration
- Add Core interface control for loadConfiguration in CoreInterface.js
- Add core management CLI command for loadConfiguration

### initializeAlwaysLoadedSprites
**File:** `src/core/SpriteEngine.js:727`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for initializeAlwaysLoadedSprites
- Add Core interface control for initializeAlwaysLoadedSprites in CoreInterface.js
- Add core management CLI command for initializeAlwaysLoadedSprites

### initializeAuditLogging
**File:** `src/core/SpriteEngine.js:741`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for initializeAuditLogging
- Add Core interface control for initializeAuditLogging in CoreInterface.js
- Add core management CLI command for initializeAuditLogging

### processConversationalRequest
**File:** `src/core/SpriteEngine.js:757`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for processConversationalRequest
- Add Core interface control for processConversationalRequest in CoreInterface.js
- Add CLI command wrapper for processConversationalRequest

### processVoiceInput
**File:** `src/core/SpriteEngine.js:792`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for processVoiceInput
- Add Core interface control for processVoiceInput in CoreInterface.js
- Add CLI command wrapper for processVoiceInput

### routeRequest
**File:** `src/core/SpriteEngine.js:812`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for routeRequest
- Add Core interface control for routeRequest in CoreInterface.js
- Add core management CLI command for routeRequest

### validateSecurity
**File:** `src/core/SpriteEngine.js:835`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for validateSecurity
- Add Core interface control for validateSecurity in CoreInterface.js
- Add core management CLI command for validateSecurity

### executeRequest
**File:** `src/core/SpriteEngine.js:862`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for executeRequest
- Add Core interface control for executeRequest in CoreInterface.js
- Add CLI command wrapper for executeRequest

### executeWithSprites
**File:** `src/core/SpriteEngine.js:891`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for executeWithSprites
- Add Core interface control for executeWithSprites in CoreInterface.js
- Add CLI command wrapper for executeWithSprites

### executeWithHeavyLLM
**File:** `src/core/SpriteEngine.js:914`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for executeWithHeavyLLM
- Add Core interface control for executeWithHeavyLLM in CoreInterface.js
- Add CLI command wrapper for executeWithHeavyLLM

### callSprite
**File:** `src/core/SpriteEngine.js:967`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for callSprite
- Add Core interface control for callSprite in CoreInterface.js
- Add core management CLI command for callSprite

### extractPersonaFromResponse
**File:** `src/core/SpriteEngine.js:1022`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for extractPersonaFromResponse
- Add Core interface control for extractPersonaFromResponse in CoreInterface.js
- Add core management CLI command for extractPersonaFromResponse

### extractEngineFromResponse
**File:** `src/core/SpriteEngine.js:1029`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for extractEngineFromResponse
- Add Core interface control for extractEngineFromResponse in CoreInterface.js
- Add core management CLI command for extractEngineFromResponse

### checkForSensitiveContent
**File:** `src/core/SpriteEngine.js:1036`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for checkForSensitiveContent
- Add Core interface control for checkForSensitiveContent in CoreInterface.js
- Add core management CLI command for checkForSensitiveContent

### loadSprite
**File:** `src/core/SpriteEngine.js:1041`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for loadSprite
- Add Core interface control for loadSprite in CoreInterface.js
- Add core management CLI command for loadSprite

### loadHeavyLLM
**File:** `src/core/SpriteEngine.js:1075`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for loadHeavyLLM
- Add Core interface control for loadHeavyLLM in CoreInterface.js
- Add core management CLI command for loadHeavyLLM

### prepareMemoryIsolation
**File:** `src/core/SpriteEngine.js:1127`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for prepareMemoryIsolation
- Add Core interface control for prepareMemoryIsolation in CoreInterface.js
- Add core management CLI command for prepareMemoryIsolation

### performHotSwap
**File:** `src/core/SpriteEngine.js:1149`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for performHotSwap
- Add Core interface control for performHotSwap in CoreInterface.js
- Add core management CLI command for performHotSwap

### gracefulEngineUnload
**File:** `src/core/SpriteEngine.js:1164`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for gracefulEngineUnload
- Add Core interface control for gracefulEngineUnload in CoreInterface.js
- Add core management CLI command for gracefulEngineUnload

### performEngineLoad
**File:** `src/core/SpriteEngine.js:1199`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for performEngineLoad
- Add Core interface control for performEngineLoad in CoreInterface.js
- Add core management CLI command for performEngineLoad

### verifyEngineHealth
**File:** `src/core/SpriteEngine.js:1242`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for verifyEngineHealth
- Add Core interface control for verifyEngineHealth in CoreInterface.js
- Add core management CLI command for verifyEngineHealth

### callModelLoadAPI
**File:** `src/core/SpriteEngine.js:1275`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for callModelLoadAPI
- Add UI button/form calling callModelLoadAPI in appropriate React component
- Add core management CLI command for callModelLoadAPI

### callModelUnloadAPI
**File:** `src/core/SpriteEngine.js:1298`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for callModelUnloadAPI
- Add UI button/form calling callModelUnloadAPI in appropriate React component
- Add core management CLI command for callModelUnloadAPI

### createSwapTimeout
**File:** `src/core/SpriteEngine.js:1321`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for createSwapTimeout
- Add Core interface control for createSwapTimeout in CoreInterface.js
- Add core management CLI command for createSwapTimeout

### unloadAllHeavyLLM
**File:** `src/core/SpriteEngine.js:1329`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for unloadAllHeavyLLM
- Add Core interface control for unloadAllHeavyLLM in CoreInterface.js
- Add core management CLI command for unloadAllHeavyLLM

### logTaskExecution
**File:** `src/core/SpriteEngine.js:1367`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for logTaskExecution
- Add Core interface control for logTaskExecution in CoreInterface.js
- Add core management CLI command for logTaskExecution

### generateTaskId
**File:** `src/core/SpriteEngine.js:1379`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for generateTaskId
- Add Core interface control for generateTaskId in CoreInterface.js
- Add core management CLI command for generateTaskId

### getSessionId
**File:** `src/core/SpriteEngine.js:1383`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getSessionId
- Add Core interface control for getSessionId in CoreInterface.js
- Add core management CLI command for getSessionId

### getActiveSprites
**File:** `src/core/SpriteEngine.js:1401`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getActiveSprites
- Add Core interface control for getActiveSprites in CoreInterface.js
- Add core management CLI command for getActiveSprites

### getLoadedEngines
**File:** `src/core/SpriteEngine.js:1410`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getLoadedEngines
- Add Core interface control for getLoadedEngines in CoreInterface.js
- Add core management CLI command for getLoadedEngines

### getHotSwapStatus
**File:** `src/core/SpriteEngine.js:1427`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getHotSwapStatus
- Add Core interface control for getHotSwapStatus in CoreInterface.js
- Add core management CLI command for getHotSwapStatus

### getLastSwapTime
**File:** `src/core/SpriteEngine.js:1446`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getLastSwapTime
- Add Core interface control for getLastSwapTime in CoreInterface.js
- Add core management CLI command for getLastSwapTime

### calculateAverageLoadTime
**File:** `src/core/SpriteEngine.js:1453`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for calculateAverageLoadTime
- Add Core interface control for calculateAverageLoadTime in CoreInterface.js
- Add core management CLI command for calculateAverageLoadTime

### updateConfiguration
**File:** `src/core/SpriteEngine.js:1461`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for updateConfiguration
- Add Core interface control for updateConfiguration in CoreInterface.js
- Add core management CLI command for updateConfiguration

### getConfiguration
**File:** `src/core/SpriteEngine.js:1467`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getConfiguration
- Add Core interface control for getConfiguration in CoreInterface.js
- Add core management CLI command for getConfiguration

### getPowerMetrics
**File:** `src/core/SpriteEngine.js:1474`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getPowerMetrics
- Add Core interface control for getPowerMetrics in CoreInterface.js
- Add core management CLI command for getPowerMetrics

### getModelActivationSummary
**File:** `src/core/SpriteEngine.js:1481`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getModelActivationSummary
- Add Core interface control for getModelActivationSummary in CoreInterface.js
- Add core management CLI command for getModelActivationSummary

### recordThermalEvent
**File:** `src/core/SpriteEngine.js:1488`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for recordThermalEvent
- Add Core interface control for recordThermalEvent in CoreInterface.js
- Add core management CLI command for recordThermalEvent

### updateMemoryUsage
**File:** `src/core/SpriteEngine.js:1495`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for updateMemoryUsage
- Add Core interface control for updateMemoryUsage in CoreInterface.js
- Add core management CLI command for updateMemoryUsage

### getTelemetryReport
**File:** `src/core/SpriteEngine.js:1502`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getTelemetryReport
- Add Core interface control for getTelemetryReport in CoreInterface.js
- Add core management CLI command for getTelemetryReport

### getPowerStatus
**File:** `src/core/SpriteEngine.js:1521`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getPowerStatus
- Add Core interface control for getPowerStatus in CoreInterface.js
- Add core management CLI command for getPowerStatus

### updatePowerBudget
**File:** `src/core/SpriteEngine.js:1528`
**Module:** `src.core.SpriteEngine`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for updatePowerBudget
- Add Core interface control for updatePowerBudget in CoreInterface.js
- Add core management CLI command for updatePowerBudget

### canLoadModel
**File:** `src/core/SpriteEngine.js:1536`
**Module:** `src.core.SpriteEngine`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for canLoadModel
- Add Core interface control for canLoadModel in CoreInterface.js
- Add core management CLI command for canLoadModel

### AldenInterface
**File:** `src/personas/alden/AldenInterface.js:7`
**Module:** `src.personas.alden.AldenInterface`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for AldenInterface
- Consider adding UI control for AldenInterface if user-facing
- Consider adding CLI command for AldenInterface if appropriate

### delegateToGoogle
**File:** `src/personas/alden/AldenInterface.js:33`
**Module:** `src.personas.alden.AldenInterface`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for delegateToGoogle
- Consider adding UI control for delegateToGoogle if user-facing
- Consider adding CLI command for delegateToGoogle if appropriate

### handleSendMessage
**File:** `src/personas/alden/AldenInterface.js:88`
**Module:** `src.personas.alden.AldenInterface`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for handleSendMessage
- Consider adding UI control for handleSendMessage if user-facing
- Consider adding CLI command for handleSendMessage if appropriate

### generateResponse
**File:** `src/personas/alden/AldenInterface.js:129`
**Module:** `src.personas.alden.AldenInterface`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for generateResponse
- Consider adding UI control for generateResponse if user-facing
- Consider adding CLI command for generateResponse if appropriate

### getRadialPosition
**File:** `src/personas/alden/AldenInterface.js:495`
**Module:** `src.personas.alden.AldenInterface`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getRadialPosition
- Consider adding UI control for getRadialPosition if user-facing
- Consider adding CLI command for getRadialPosition if appropriate

### renderScreen
**File:** `src/personas/alden/AldenInterface.js:502`
**Module:** `src.personas.alden.AldenInterface`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for renderScreen
- Consider adding UI control for renderScreen if user-facing
- Consider adding CLI command for renderScreen if appropriate

### refill
**File:** `services/metrics.ts:22`
**Module:** `services.metrics`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for refill
- Consider adding UI control for refill if user-facing
- Consider adding CLI command for refill if appropriate

### canMakeRequest
**File:** `services/metrics.ts:31`
**Module:** `services.metrics`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for canMakeRequest
- Consider adding UI control for canMakeRequest if user-facing
- Consider adding CLI command for canMakeRequest if appropriate

### addRequest
**File:** `services/metrics.ts:36`
**Module:** `services.metrics`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for addRequest
- Consider adding UI control for addRequest if user-facing
- Consider adding CLI command for addRequest if appropriate

### getWaitTime
**File:** `services/metrics.ts:44`
**Module:** `services.metrics`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getWaitTime
- Consider adding UI control for getWaitTime if user-facing
- Consider adding CLI command for getWaitTime if appropriate

### getRemainingRequests
**File:** `services/metrics.ts:49`
**Module:** `services.metrics`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getRemainingRequests
- Consider adding UI control for getRemainingRequests if user-facing
- Consider adding CLI command for getRemainingRequests if appropriate

### startSession
**File:** `services/metrics.ts:77`
**Module:** `services.metrics`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for startSession
- Consider adding UI control for startSession if user-facing
- Consider adding CLI command for startSession if appropriate

### addDelegation
**File:** `services/metrics.ts:91`
**Module:** `services.metrics`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for addDelegation
- Consider adding UI control for addDelegation if user-facing
- Consider adding CLI command for addDelegation if appropriate

### endSession
**File:** `services/metrics.ts:110`
**Module:** `services.metrics`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for endSession
- Consider adding UI control for endSession if user-facing
- Consider adding CLI command for endSession if appropriate

### updateGlobalMetrics
**File:** `services/metrics.ts:125`
**Module:** `services.metrics`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for updateGlobalMetrics
- Consider adding UI control for updateGlobalMetrics if user-facing
- Consider adding CLI command for updateGlobalMetrics if appropriate

### queuePersistence
**File:** `services/metrics.ts:146`
**Module:** `services.metrics`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for queuePersistence
- Consider adding UI control for queuePersistence if user-facing
- Consider adding CLI command for queuePersistence if appropriate

### processQueue
**File:** `services/metrics.ts:154`
**Module:** `services.metrics`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for processQueue
- Consider adding UI control for processQueue if user-facing
- Add CLI command wrapper for processQueue

### persistItem
**File:** `services/metrics.ts:170`
**Module:** `services.metrics`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for persistItem
- Consider adding UI control for persistItem if user-facing
- Consider adding CLI command for persistItem if appropriate

### compressOldData
**File:** `services/metrics.ts:217`
**Module:** `services.metrics`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for compressOldData
- Consider adding UI control for compressOldData if user-facing
- Consider adding CLI command for compressOldData if appropriate

### getMetrics
**File:** `services/metrics.ts:259`
**Module:** `services.metrics`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getMetrics
- Consider adding UI control for getMetrics if user-facing
- Consider adding CLI command for getMetrics if appropriate

### getCachedExists
**File:** `services/protocolHandler.ts:10`
**Module:** `services.protocolHandler`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getCachedExists
- Consider adding UI control for getCachedExists if user-facing
- Consider adding CLI command for getCachedExists if appropriate

### getCachedExists
**File:** `services/protocolHandler.ts:10`
**Module:** `services.protocolHandler`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getCachedExists
- Consider adding UI control for getCachedExists if user-facing
- Consider adding CLI command for getCachedExists if appropriate

### setCachedExists
**File:** `services/protocolHandler.ts:18`
**Module:** `services.protocolHandler`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for setCachedExists
- Consider adding UI control for setCachedExists if user-facing
- Consider adding CLI command for setCachedExists if appropriate

### setCachedExists
**File:** `services/protocolHandler.ts:18`
**Module:** `services.protocolHandler`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for setCachedExists
- Consider adding UI control for setCachedExists if user-facing
- Consider adding CLI command for setCachedExists if appropriate

### checkFileExists
**File:** `services/protocolHandler.ts:25`
**Module:** `services.protocolHandler`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for checkFileExists
- Consider adding UI control for checkFileExists if user-facing
- Consider adding CLI command for checkFileExists if appropriate

### checkFileExists
**File:** `services/protocolHandler.ts:25`
**Module:** `services.protocolHandler`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for checkFileExists
- Consider adding UI control for checkFileExists if user-facing
- Consider adding CLI command for checkFileExists if appropriate

### registerProtocolHandler
**File:** `services/protocolHandler.ts:40`
**Module:** `services.protocolHandler`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for registerProtocolHandler
- Consider adding UI control for registerProtocolHandler if user-facing
- Consider adding CLI command for registerProtocolHandler if appropriate

### validatePythonPath
**File:** `services/pythonBridge.ts:10`
**Module:** `services.pythonBridge`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for validatePythonPath
- Consider adding UI control for validatePythonPath if user-facing
- Consider adding CLI command for validatePythonPath if appropriate

### validatePythonPath
**File:** `services/pythonBridge.ts:10`
**Module:** `services.pythonBridge`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for validatePythonPath
- Consider adding UI control for validatePythonPath if user-facing
- Consider adding CLI command for validatePythonPath if appropriate

### startPythonBackend
**File:** `services/pythonBridge.ts:47`
**Module:** `services.pythonBridge`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for startPythonBackend
- Consider adding UI control for startPythonBackend if user-facing
- Consider adding CLI command for startPythonBackend if appropriate

### startPythonBackend
**File:** `services/pythonBridge.ts:47`
**Module:** `services.pythonBridge`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for startPythonBackend
- Consider adding UI control for startPythonBackend if user-facing
- Consider adding CLI command for startPythonBackend if appropriate

### responseHandler
**File:** `services/pythonBridge.ts:133`
**Module:** `services.pythonBridge`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for responseHandler
- Consider adding UI control for responseHandler if user-facing
- Consider adding CLI command for responseHandler if appropriate

### stopPythonBackend
**File:** `services/pythonBridge.ts:150`
**Module:** `services.pythonBridge`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for stopPythonBackend
- Consider adding UI control for stopPythonBackend if user-facing
- Consider adding CLI command for stopPythonBackend if appropriate

### stopPythonBackend
**File:** `services/pythonBridge.ts:150`
**Module:** `services.pythonBridge`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for stopPythonBackend
- Consider adding UI control for stopPythonBackend if user-facing
- Consider adding CLI command for stopPythonBackend if appropriate

### getPythonProcess
**File:** `services/pythonBridge.ts:157`
**Module:** `services.pythonBridge`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getPythonProcess
- Consider adding UI control for getPythonProcess if user-facing
- Add CLI command wrapper for getPythonProcess

### getPythonProcess
**File:** `services/pythonBridge.ts:157`
**Module:** `services.pythonBridge`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getPythonProcess
- Consider adding UI control for getPythonProcess if user-facing
- Add CLI command wrapper for getPythonProcess

### getCachedStat
**File:** `services/staticServer.ts:13`
**Module:** `services.staticServer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getCachedStat
- Consider adding UI control for getCachedStat if user-facing
- Consider adding CLI command for getCachedStat if appropriate

### getCachedStat
**File:** `services/staticServer.ts:13`
**Module:** `services.staticServer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getCachedStat
- Consider adding UI control for getCachedStat if user-facing
- Consider adding CLI command for getCachedStat if appropriate

### setCachedStat
**File:** `services/staticServer.ts:21`
**Module:** `services.staticServer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for setCachedStat
- Consider adding UI control for setCachedStat if user-facing
- Consider adding CLI command for setCachedStat if appropriate

### setCachedStat
**File:** `services/staticServer.ts:21`
**Module:** `services.staticServer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for setCachedStat
- Consider adding UI control for setCachedStat if user-facing
- Consider adding CLI command for setCachedStat if appropriate

### checkFileExists
**File:** `services/staticServer.ts:28`
**Module:** `services.staticServer`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for checkFileExists
- Consider adding UI control for checkFileExists if user-facing
- Consider adding CLI command for checkFileExists if appropriate

### checkFileExists
**File:** `services/staticServer.ts:28`
**Module:** `services.staticServer`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for checkFileExists
- Consider adding UI control for checkFileExists if user-facing
- Consider adding CLI command for checkFileExists if appropriate

### startStaticServer
**File:** `services/staticServer.ts:42`
**Module:** `services.staticServer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for startStaticServer
- Consider adding UI control for startStaticServer if user-facing
- Consider adding CLI command for startStaticServer if appropriate

### startStaticServer
**File:** `services/staticServer.ts:42`
**Module:** `services.staticServer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for startStaticServer
- Consider adding UI control for startStaticServer if user-facing
- Consider adding CLI command for startStaticServer if appropriate

### stopStaticServer
**File:** `services/staticServer.ts:146`
**Module:** `services.staticServer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for stopStaticServer
- Consider adding UI control for stopStaticServer if user-facing
- Consider adding CLI command for stopStaticServer if appropriate

### stopStaticServer
**File:** `services/staticServer.ts:146`
**Module:** `services.staticServer`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for stopStaticServer
- Consider adding UI control for stopStaticServer if user-facing
- Consider adding CLI command for stopStaticServer if appropriate

### resolveConflict
**File:** `services/memory-sync/conflict-policies.js:56`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for resolveConflict
- Consider adding UI control for resolveConflict if user-facing
- Consider adding CLI command for resolveConflict if appropriate

### applyResolutionPolicies
**File:** `services/memory-sync/conflict-policies.js:87`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for applyResolutionPolicies
- Consider adding UI control for applyResolutionPolicies if user-facing
- Consider adding CLI command for applyResolutionPolicies if appropriate

### securityOverridePolicy
**File:** `services/memory-sync/conflict-policies.js:120`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for securityOverridePolicy
- Consider adding UI control for securityOverridePolicy if user-facing
- Consider adding CLI command for securityOverridePolicy if appropriate

### emergencyTagPolicy
**File:** `services/memory-sync/conflict-policies.js:162`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for emergencyTagPolicy
- Consider adding UI control for emergencyTagPolicy if user-facing
- Consider adding CLI command for emergencyTagPolicy if appropriate

### agentPriorityPolicy
**File:** `services/memory-sync/conflict-policies.js:194`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for agentPriorityPolicy
- Consider adding UI control for agentPriorityPolicy if user-facing
- Consider adding CLI command for agentPriorityPolicy if appropriate

### customTagPolicy
**File:** `services/memory-sync/conflict-policies.js:230`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for customTagPolicy
- Consider adding UI control for customTagPolicy if user-facing
- Consider adding CLI command for customTagPolicy if appropriate

### getHighestTagPriority
**File:** `services/memory-sync/conflict-policies.js:234`
**Module:** `services.memory-sync.conflict-policies`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getHighestTagPriority
- Consider adding UI control for getHighestTagPriority if user-facing
- Consider adding CLI command for getHighestTagPriority if appropriate

### recencyBiasPolicy
**File:** `services/memory-sync/conflict-policies.js:271`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for recencyBiasPolicy
- Consider adding UI control for recencyBiasPolicy if user-facing
- Consider adding CLI command for recencyBiasPolicy if appropriate

### timestampPolicy
**File:** `services/memory-sync/conflict-policies.js:293`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for timestampPolicy
- Consider adding UI control for timestampPolicy if user-facing
- Consider adding CLI command for timestampPolicy if appropriate

### weightedImportancePolicy
**File:** `services/memory-sync/conflict-policies.js:317`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for weightedImportancePolicy
- Consider adding UI control for weightedImportancePolicy if user-facing
- Consider adding CLI command for weightedImportancePolicy if appropriate

### sessionContinuityPolicy
**File:** `services/memory-sync/conflict-policies.js:352`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for sessionContinuityPolicy
- Consider adding UI control for sessionContinuityPolicy if user-facing
- Consider adding CLI command for sessionContinuityPolicy if appropriate

### contentMergePolicy
**File:** `services/memory-sync/conflict-policies.js:372`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for contentMergePolicy
- Consider adding UI control for contentMergePolicy if user-facing
- Consider adding CLI command for contentMergePolicy if appropriate

### stabilityFallbackPolicy
**File:** `services/memory-sync/conflict-policies.js:396`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for stabilityFallbackPolicy
- Consider adding UI control for stabilityFallbackPolicy if user-facing
- Consider adding CLI command for stabilityFallbackPolicy if appropriate

### canMergeContent
**File:** `services/memory-sync/conflict-policies.js:416`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for canMergeContent
- Consider adding UI control for canMergeContent if user-facing
- Consider adding CLI command for canMergeContent if appropriate

### mergeContent
**File:** `services/memory-sync/conflict-policies.js:434`
**Module:** `services.memory-sync.conflict-policies`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for mergeContent
- Consider adding UI control for mergeContent if user-facing
- Consider adding CLI command for mergeContent if appropriate

### calculateContentSimilarity
**File:** `services/memory-sync/conflict-policies.js:459`
**Module:** `services.memory-sync.conflict-policies`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for calculateContentSimilarity
- Consider adding UI control for calculateContentSimilarity if user-facing
- Consider adding CLI command for calculateContentSimilarity if appropriate

### updateResolutionStats
**File:** `services/memory-sync/conflict-policies.js:477`
**Module:** `services.memory-sync.conflict-policies`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for updateResolutionStats
- Consider adding UI control for updateResolutionStats if user-facing
- Consider adding CLI command for updateResolutionStats if appropriate

### getResolutionStats
**File:** `services/memory-sync/conflict-policies.js:490`
**Module:** `services.memory-sync.conflict-policies`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getResolutionStats
- Consider adding UI control for getResolutionStats if user-facing
- Consider adding CLI command for getResolutionStats if appropriate

### getTagPriority
**File:** `services/memory-sync/index.js:111`
**Module:** `services.memory-sync.index`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getTagPriority
- Consider adding UI control for getTagPriority if user-facing
- Consider adding CLI command for getTagPriority if appropriate

### calculateContentSimilarity
**File:** `services/memory-sync/index.js:141`
**Module:** `services.memory-sync.index`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for calculateContentSimilarity
- Consider adding UI control for calculateContentSimilarity if user-facing
- Consider adding CLI command for calculateContentSimilarity if appropriate

### calculateContentSimilarity
**File:** `services/memory-sync/index.js:141`
**Module:** `services.memory-sync.index`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for calculateContentSimilarity
- Consider adding UI control for calculateContentSimilarity if user-facing
- Consider adding CLI command for calculateContentSimilarity if appropriate

### mergeContent
**File:** `services/memory-sync/index.js:156`
**Module:** `services.memory-sync.index`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for mergeContent
- Consider adding UI control for mergeContent if user-facing
- Consider adding CLI command for mergeContent if appropriate

### mergeContent
**File:** `services/memory-sync/index.js:156`
**Module:** `services.memory-sync.index`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for mergeContent
- Consider adding UI control for mergeContent if user-facing
- Consider adding CLI command for mergeContent if appropriate

### determineResolutionStrategy
**File:** `services/memory-sync/index.js:498`
**Module:** `services.memory-sync.index`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for determineResolutionStrategy
- Consider adding UI control for determineResolutionStrategy if user-facing
- Consider adding CLI command for determineResolutionStrategy if appropriate

### attemptAutoResolution
**File:** `services/memory-sync/index.js:510`
**Module:** `services.memory-sync.index`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for attemptAutoResolution
- Consider adding UI control for attemptAutoResolution if user-facing
- Consider adding CLI command for attemptAutoResolution if appropriate

### resolveByImportance
**File:** `services/memory-sync/index.js:631`
**Module:** `services.memory-sync.index`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for resolveByImportance
- Consider adding UI control for resolveByImportance if user-facing
- Consider adding CLI command for resolveByImportance if appropriate

### mergeMemoryContent
**File:** `services/memory-sync/index.js:654`
**Module:** `services.memory-sync.index`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for mergeMemoryContent
- Consider adding UI control for mergeMemoryContent if user-facing
- Consider adding CLI command for mergeMemoryContent if appropriate

### validateSyncData
**File:** `services/memory-sync/index.js:784`
**Module:** `services.memory-sync.index`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for validateSyncData
- Consider adding UI control for validateSyncData if user-facing
- Consider adding CLI command for validateSyncData if appropriate

### updateMetrics
**File:** `services/memory-sync/index.js:803`
**Module:** `services.memory-sync.index`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for updateMetrics
- Consider adding UI control for updateMetrics if user-facing
- Consider adding CLI command for updateMetrics if appropriate

### getSyncStatus
**File:** `services/memory-sync/index.js:818`
**Module:** `services.memory-sync.index`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getSyncStatus
- Consider adding UI control for getSyncStatus if user-facing
- Consider adding CLI command for getSyncStatus if appropriate

### forceMemorySync
**File:** `services/memory-sync/index.js:837`
**Module:** `services.memory-sync.index`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for forceMemorySync
- Consider adding UI control for forceMemorySync if user-facing
- Consider adding CLI command for forceMemorySync if appropriate

### startConflictProcessor
**File:** `services/memory-sync/index.js:887`
**Module:** `services.memory-sync.index`
**Type:** function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for startConflictProcessor
- Consider adding UI control for startConflictProcessor if user-facing
- Add CLI command wrapper for startConflictProcessor

### processActiveConflicts
**File:** `services/memory-sync/index.js:898`
**Module:** `services.memory-sync.index`
**Type:** async_function
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for processActiveConflicts
- Consider adding UI control for processActiveConflicts if user-facing
- Add CLI command wrapper for processActiveConflicts

### GET /api/v1/alden/message
**File:** `src/api/alden_api.py:162`
**Module:** `src.api.alden_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/v1/alden/message
- Add UI button/form calling GET /api/v1/alden/message in appropriate React component

### GET /api/v1/alden/traits/{trait_name}
**File:** `src/api/alden_api.py:201`
**Module:** `src.api.alden_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/v1/alden/traits/{trait_name}
- Add UI button/form calling GET /api/v1/alden/traits/{trait_name} in appropriate React component

### GET /api/v1/alden/corrections
**File:** `src/api/alden_api.py:230`
**Module:** `src.api.alden_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/v1/alden/corrections
- Add UI button/form calling GET /api/v1/alden/corrections in appropriate React component

### GET /api/v1/alden/mood
**File:** `src/api/alden_api.py:259`
**Module:** `src.api.alden_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/v1/alden/mood
- Add UI button/form calling GET /api/v1/alden/mood in appropriate React component

### GET /api/v1/alden/memory/export
**File:** `src/api/alden_api.py:309`
**Module:** `src.api.alden_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/v1/alden/memory/export
- Add UI button/form calling GET /api/v1/alden/memory/export in appropriate React component

### GET /api/agents
**File:** `src/api/core_api.py:287`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/agents
- Add UI button/form calling GET /api/agents in appropriate React component

### PUT /api/agents/<agent_id>
**File:** `src/api/core_api.py:309`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting PUT /api/agents/<agent_id>
- Add UI button/form calling PUT /api/agents/<agent_id> in appropriate React component

### GET /api/services
**File:** `src/api/core_api.py:323`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/services
- Add UI button/form calling GET /api/services in appropriate React component

### GET /api/services/<service_id>/health
**File:** `src/api/core_api.py:334`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/services/<service_id>/health
- Add UI button/form calling GET /api/services/<service_id>/health in appropriate React component

### GET /api/projects
**File:** `src/api/core_api.py:354`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/projects
- Add UI button/form calling GET /api/projects in appropriate React component

### POST /api/projects
**File:** `src/api/core_api.py:362`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/projects
- Add UI button/form calling POST /api/projects in appropriate React component

### GET /api/projects/<project_id>
**File:** `src/api/core_api.py:391`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/projects/<project_id>
- Add UI button/form calling GET /api/projects/<project_id> in appropriate React component

### POST /api/projects/<project_id>/orchestrate
**File:** `src/api/core_api.py:399`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/projects/<project_id>/orchestrate
- Add UI button/form calling POST /api/projects/<project_id>/orchestrate in appropriate React component

### POST /api/projects/<project_id>/tasks/<task_id>/delegate
**File:** `src/api/core_api.py:422`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/projects/<project_id>/tasks/<task_id>/delegate
- Add UI button/form calling POST /api/projects/<project_id>/tasks/<task_id>/delegate in appropriate React component

### GET /api/sessions
**File:** `src/api/core_api.py:445`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/sessions
- Add UI button/form calling GET /api/sessions in appropriate React component

### POST /api/sessions/<session_id>/join
**File:** `src/api/core_api.py:487`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/sessions/<session_id>/join
- Add UI button/form calling POST /api/sessions/<session_id>/join in appropriate React component

### POST /api/sessions/<session_id>/message
**File:** `src/api/core_api.py:511`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/sessions/<session_id>/message
- Add UI button/form calling POST /api/sessions/<session_id>/message in appropriate React component

### GET /api/orchestration/status
**File:** `src/api/core_api.py:533`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/orchestration/status
- Add UI button/form calling GET /api/orchestration/status in appropriate React component

### GET /api/orchestration/logs
**File:** `src/api/core_api.py:549`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/orchestration/logs
- Add UI button/form calling GET /api/orchestration/logs in appropriate React component

### GET /api/system/memory
**File:** `src/api/core_api.py:570`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/system/memory
- Add UI button/form calling GET /api/system/memory in appropriate React component

### GET /api/system/health
**File:** `src/api/core_api.py:622`
**Module:** `src.api.core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/system/health
- Add UI button/form calling GET /api/system/health in appropriate React component

### GET /session/agentic
**File:** `src/api/enhanced_core_api.py:86`
**Module:** `src.api.enhanced_core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /session/agentic
- Add UI button/form calling GET /session/agentic in appropriate React component

### GET /task/agentic
**File:** `src/api/enhanced_core_api.py:111`
**Module:** `src.api.enhanced_core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /task/agentic
- Add UI button/form calling GET /task/agentic in appropriate React component

### GET /task/delegate
**File:** `src/api/enhanced_core_api.py:146`
**Module:** `src.api.enhanced_core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /task/delegate
- Add UI button/form calling GET /task/delegate in appropriate React component

### GET /agents/capabilities
**File:** `src/api/enhanced_core_api.py:176`
**Module:** `src.api.enhanced_core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /agents/capabilities
- Add UI button/form calling GET /agents/capabilities in appropriate React component

### GET /workflows/status
**File:** `src/api/enhanced_core_api.py:191`
**Module:** `src.api.enhanced_core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /workflows/status
- Add UI button/form calling GET /workflows/status in appropriate React component

### GET /workflow/control
**File:** `src/api/enhanced_core_api.py:216`
**Module:** `src.api.enhanced_core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /workflow/control
- Add UI button/form calling GET /workflow/control in appropriate React component

### GET /session/{session_id}/enhanced
**File:** `src/api/enhanced_core_api.py:244`
**Module:** `src.api.enhanced_core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /session/{session_id}/enhanced
- Add UI button/form calling GET /session/{session_id}/enhanced in appropriate React component

### GET /session/{session_id}/workflows
**File:** `src/api/enhanced_core_api.py:264`
**Module:** `src.api.enhanced_core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /session/{session_id}/workflows
- Add UI button/form calling GET /session/{session_id}/workflows in appropriate React component

### GET /agents/{agent_id}/delegations
**File:** `src/api/enhanced_core_api.py:300`
**Module:** `src.api.enhanced_core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /agents/{agent_id}/delegations
- Add UI button/form calling GET /agents/{agent_id}/delegations in appropriate React component

### GET /agents/suggest
**File:** `src/api/enhanced_core_api.py:329`
**Module:** `src.api.enhanced_core_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /agents/suggest
- Add UI button/form calling GET /agents/suggest in appropriate React component

### GET /api/external-agents
**File:** `src/api/external_agent_api.py:162`
**Module:** `src.api.external_agent_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/external-agents
- Add UI button/form calling GET /api/external-agents in appropriate React component

### GET /api/external-agents/<agent_id>/status
**File:** `src/api/external_agent_api.py:197`
**Module:** `src.api.external_agent_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/external-agents/<agent_id>/status
- Add UI button/form calling GET /api/external-agents/<agent_id>/status in appropriate React component

### POST /api/external-agents/<agent_id>/execute
**File:** `src/api/external_agent_api.py:226`
**Module:** `src.api.external_agent_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/external-agents/<agent_id>/execute
- Add UI button/form calling POST /api/external-agents/<agent_id>/execute in appropriate React component

### POST /api/external-agents/<agent_id>/generate
**File:** `src/api/external_agent_api.py:263`
**Module:** `src.api.external_agent_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/external-agents/<agent_id>/generate
- Add UI button/form calling POST /api/external-agents/<agent_id>/generate in appropriate React component

### POST /api/external-agents/<agent_id>/files/write
**File:** `src/api/external_agent_api.py:309`
**Module:** `src.api.external_agent_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/external-agents/<agent_id>/files/write
- Add UI button/form calling POST /api/external-agents/<agent_id>/files/write in appropriate React component

### POST /api/external-agents/<agent_id>/files/read
**File:** `src/api/external_agent_api.py:355`
**Module:** `src.api.external_agent_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/external-agents/<agent_id>/files/read
- Add UI button/form calling POST /api/external-agents/<agent_id>/files/read in appropriate React component

### GET /api/external-agents/<agent_id>/files/list
**File:** `src/api/external_agent_api.py:399`
**Module:** `src.api.external_agent_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/external-agents/<agent_id>/files/list
- Add UI button/form calling GET /api/external-agents/<agent_id>/files/list in appropriate React component

### GET /api/external-agents/circuit-breakers/status
**File:** `src/api/external_agent_api.py:437`
**Module:** `src.api.external_agent_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/external-agents/circuit-breakers/status
- Add UI button/form calling GET /api/external-agents/circuit-breakers/status in appropriate React component

### POST /api/external-agents/circuit-breakers/<service_name>/reset
**File:** `src/api/external_agent_api.py:450`
**Module:** `src.api.external_agent_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/external-agents/circuit-breakers/<service_name>/reset
- Add UI button/form calling POST /api/external-agents/circuit-breakers/<service_name>/reset in appropriate React component

### POST /api/external-agents/circuit-breakers/reset-all
**File:** `src/api/external_agent_api.py:475`
**Module:** `src.api.external_agent_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/external-agents/circuit-breakers/reset-all
- Add UI button/form calling POST /api/external-agents/circuit-breakers/reset-all in appropriate React component

### GET /agentic
**File:** `src/api/kimi_k2_api.py:204`
**Module:** `src.api.kimi_k2_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /agentic
- Add UI button/form calling GET /agentic in appropriate React component

### GET /long-context
**File:** `src/api/kimi_k2_api.py:247`
**Module:** `src.api.kimi_k2_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /long-context
- Add UI button/form calling GET /long-context in appropriate React component

### GET /stats
**File:** `src/api/kimi_k2_api.py:314`
**Module:** `src.api.kimi_k2_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /stats
- Add UI button/form calling GET /stats in appropriate React component

### GET /capabilities
**File:** `src/api/kimi_k2_api.py:338`
**Module:** `src.api.kimi_k2_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /capabilities
- Add UI button/form calling GET /capabilities in appropriate React component

### GET /estimate-cost
**File:** `src/api/kimi_k2_api.py:365`
**Module:** `src.api.kimi_k2_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /estimate-cost
- Add UI button/form calling GET /estimate-cost in appropriate React component

### GET /license-info/{template_id}
**File:** `src/api/license_validation.py:326`
**Module:** `src.api.license_validation`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /license-info/{template_id}
- Add UI button/form calling GET /license-info/{template_id} in appropriate React component

### GET /user-licenses/{user_id}
**File:** `src/api/license_validation.py:353`
**Module:** `src.api.license_validation`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /user-licenses/{user_id}
- Add UI button/form calling GET /user-licenses/{user_id} in appropriate React component

### GET /api/models
**File:** `src/api/local_llm_api.py:279`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/models
- Add UI button/form calling GET /api/models in appropriate React component

### POST /api/models/pull
**File:** `src/api/local_llm_api.py:309`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/models/pull
- Add UI button/form calling POST /api/models/pull in appropriate React component

### GET /api/profiles
**File:** `src/api/local_llm_api.py:436`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/profiles
- Add UI button/form calling GET /api/profiles in appropriate React component

### PUT /api/profiles
**File:** `src/api/local_llm_api.py:441`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting PUT /api/profiles
- Add UI button/form calling PUT /api/profiles in appropriate React component

### GET /api/recommendations
**File:** `src/api/local_llm_api.py:535`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/recommendations
- Add UI button/form calling GET /api/recommendations in appropriate React component

### GET /api/connection-pool
**File:** `src/api/local_llm_api.py:699`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/connection-pool
- Add UI button/form calling GET /api/connection-pool in appropriate React component

### GET /api/system-specs
**File:** `src/api/local_llm_api.py:743`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/system-specs
- Add UI button/form calling GET /api/system-specs in appropriate React component

### POST /api/websocket/repair
**File:** `src/api/local_llm_api.py:796`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/websocket/repair
- Add UI button/form calling POST /api/websocket/repair in appropriate React component

### GET /api/offline/status
**File:** `src/api/local_llm_api.py:822`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/offline/status
- Add UI button/form calling GET /api/offline/status in appropriate React component

### POST /api/offline/models/download
**File:** `src/api/local_llm_api.py:840`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/offline/models/download
- Add UI button/form calling POST /api/offline/models/download in appropriate React component

### POST /api/offline/generate
**File:** `src/api/local_llm_api.py:885`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/offline/generate
- Add UI button/form calling POST /api/offline/generate in appropriate React component

### GET /api/offline/models/cache
**File:** `src/api/local_llm_api.py:915`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/offline/models/cache
- Add UI button/form calling GET /api/offline/models/cache in appropriate React component

### POST /api/offline/models/cleanup
**File:** `src/api/local_llm_api.py:947`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/offline/models/cleanup
- Add UI button/form calling POST /api/offline/models/cleanup in appropriate React component

### POST /api/offline/emergency
**File:** `src/api/local_llm_api.py:972`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/offline/emergency
- Add UI button/form calling POST /api/offline/emergency in appropriate React component

### GET /api/circuit-breakers/status
**File:** `src/api/local_llm_api.py:994`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/circuit-breakers/status
- Add UI button/form calling GET /api/circuit-breakers/status in appropriate React component

### POST /api/circuit-breakers/<service_name>/reset
**File:** `src/api/local_llm_api.py:1007`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/circuit-breakers/<service_name>/reset
- Add UI button/form calling POST /api/circuit-breakers/<service_name>/reset in appropriate React component

### POST /api/circuit-breakers/reset-all
**File:** `src/api/local_llm_api.py:1032`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/circuit-breakers/reset-all
- Add UI button/form calling POST /api/circuit-breakers/reset-all in appropriate React component

### POST /api/settings
**File:** `src/api/local_llm_api.py:1051`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/settings
- Add UI button/form calling POST /api/settings in appropriate React component

### GET /api/settings
**File:** `src/api/local_llm_api.py:1093`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/settings
- Add UI button/form calling GET /api/settings in appropriate React component

### GET /api/claude-code/status
**File:** `src/api/local_llm_api.py:1129`
**Module:** `src.api.local_llm_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/claude-code/status
- Add UI button/form calling GET /api/claude-code/status in appropriate React component

### GET /smoke-tests
**File:** `src/api/metrics.py:185`
**Module:** `src.api.metrics`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /smoke-tests
- Add UI button/form calling GET /smoke-tests in appropriate React component

### GET /load-tests
**File:** `src/api/metrics.py:203`
**Module:** `src.api.metrics`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /load-tests
- Add UI button/form calling GET /load-tests in appropriate React component

### GET /system-health
**File:** `src/api/metrics.py:221`
**Module:** `src.api.metrics`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /system-health
- Add UI button/form calling GET /system-health in appropriate React component

### GET /spec2-compliance
**File:** `src/api/metrics.py:233`
**Module:** `src.api.metrics`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /spec2-compliance
- Add UI button/form calling GET /spec2-compliance in appropriate React component

### GET /run-smoke-tests
**File:** `src/api/metrics.py:268`
**Module:** `src.api.metrics`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /run-smoke-tests
- Add UI button/form calling GET /run-smoke-tests in appropriate React component

### GET /run-load-tests
**File:** `src/api/metrics.py:303`
**Module:** `src.api.metrics`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /run-load-tests
- Add UI button/form calling GET /run-load-tests in appropriate React component

### GET /real-time
**File:** `src/api/metrics.py:339`
**Module:** `src.api.metrics`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /real-time
- Add UI button/form calling GET /real-time in appropriate React component

### GET /dashboard-summary
**File:** `src/api/metrics.py:365`
**Module:** `src.api.metrics`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /dashboard-summary
- Add UI button/form calling GET /dashboard-summary in appropriate React component

### GET /trigger-test-suite
**File:** `src/api/metrics.py:392`
**Module:** `src.api.metrics`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /trigger-test-suite
- Add UI button/form calling GET /trigger-test-suite in appropriate React component

### GET /api/mimic/persona/{persona_id}/plugins
**File:** `src/api/mimic_api.py:450`
**Module:** `src.api.mimic_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/mimic/persona/{persona_id}/plugins
- Add UI button/form calling GET /api/mimic/persona/{persona_id}/plugins in appropriate React component

### GET /api/mimic/persona/{persona_id}/knowledge
**File:** `src/api/mimic_api.py:475`
**Module:** `src.api.mimic_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/mimic/persona/{persona_id}/knowledge
- Add UI button/form calling GET /api/mimic/persona/{persona_id}/knowledge in appropriate React component

### GET /api/mimic/persona/{persona_id}/knowledge
**File:** `src/api/mimic_api.py:515`
**Module:** `src.api.mimic_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/mimic/persona/{persona_id}/knowledge
- Add UI button/form calling GET /api/mimic/persona/{persona_id}/knowledge in appropriate React component

### GET /api/mimic/persona/{persona_id}/status
**File:** `src/api/mimic_api.py:540`
**Module:** `src.api.mimic_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/mimic/persona/{persona_id}/status
- Add UI button/form calling GET /api/mimic/persona/{persona_id}/status in appropriate React component

### GET /api/mimic/persona/{persona_id}/export
**File:** `src/api/mimic_api.py:590`
**Module:** `src.api.mimic_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/mimic/persona/{persona_id}/export
- Add UI button/form calling GET /api/mimic/persona/{persona_id}/export in appropriate React component

### GET /api/mimic/persona/{persona_id}/import
**File:** `src/api/mimic_api.py:615`
**Module:** `src.api.mimic_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/mimic/persona/{persona_id}/import
- Add UI button/form calling GET /api/mimic/persona/{persona_id}/import in appropriate React component

### GET /api/mimic/personas
**File:** `src/api/mimic_api.py:642`
**Module:** `src.api.mimic_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/mimic/personas
- Add UI button/form calling GET /api/mimic/personas in appropriate React component

### GET /api/mimic/persona/{persona_id}
**File:** `src/api/mimic_api.py:671`
**Module:** `src.api.mimic_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/mimic/persona/{persona_id}
- Add UI button/form calling GET /api/mimic/persona/{persona_id} in appropriate React component

### GET /api/sentry/system-health
**File:** `src/api/sentry_api.py:413`
**Module:** `src.api.sentry_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/sentry/system-health
- Add UI button/form calling GET /api/sentry/system-health in appropriate React component

### GET /api/sentry/events
**File:** `src/api/sentry_api.py:418`
**Module:** `src.api.sentry_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/sentry/events
- Add UI button/form calling GET /api/sentry/events in appropriate React component

### GET /api/sentry/alerts
**File:** `src/api/sentry_api.py:427`
**Module:** `src.api.sentry_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/sentry/alerts
- Add UI button/form calling GET /api/sentry/alerts in appropriate React component

### POST /api/sentry/alerts/<alert_id>/acknowledge
**File:** `src/api/sentry_api.py:439`
**Module:** `src.api.sentry_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/sentry/alerts/<alert_id>/acknowledge
- Add UI button/form calling POST /api/sentry/alerts/<alert_id>/acknowledge in appropriate React component

### POST /api/sentry/alerts/<alert_id>/resolve
**File:** `src/api/sentry_api.py:450`
**Module:** `src.api.sentry_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/sentry/alerts/<alert_id>/resolve
- Add UI button/form calling POST /api/sentry/alerts/<alert_id>/resolve in appropriate React component

### POST /api/sentry/start
**File:** `src/api/sentry_api.py:461`
**Module:** `src.api.sentry_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/sentry/start
- Add UI button/form calling POST /api/sentry/start in appropriate React component

### POST /api/sentry/stop
**File:** `src/api/sentry_api.py:467`
**Module:** `src.api.sentry_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/sentry/stop
- Add UI button/form calling POST /api/sentry/stop in appropriate React component

### GET /api/sentry/status
**File:** `src/api/sentry_api.py:473`
**Module:** `src.api.sentry_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/sentry/status
- Add UI button/form calling GET /api/sentry/status in appropriate React component

### GET /api/settings
**File:** `src/api/settings_api.py:136`
**Module:** `src.api.settings_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/settings
- Add UI button/form calling GET /api/settings in appropriate React component

### POST /api/settings
**File:** `src/api/settings_api.py:142`
**Module:** `src.api.settings_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/settings
- Add UI button/form calling POST /api/settings in appropriate React component

### POST /api/test/google-ai
**File:** `src/api/settings_api.py:154`
**Module:** `src.api.settings_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/test/google-ai
- Add UI button/form calling POST /api/test/google-ai in appropriate React component

### POST /api/test/claude-code
**File:** `src/api/settings_api.py:199`
**Module:** `src.api.settings_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/test/claude-code
- Add UI button/form calling POST /api/test/claude-code in appropriate React component

### POST /api/test/ollama
**File:** `src/api/settings_api.py:256`
**Module:** `src.api.settings_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/test/ollama
- Add UI button/form calling POST /api/test/ollama in appropriate React component

### POST /api/test/local-llm
**File:** `src/api/settings_api.py:290`
**Module:** `src.api.settings_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/test/local-llm
- Add UI button/form calling POST /api/test/local-llm in appropriate React component

### GET /api/models/ollama
**File:** `src/api/settings_api.py:340`
**Module:** `src.api.settings_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/models/ollama
- Add UI button/form calling GET /api/models/ollama in appropriate React component

### GET /api/project/services
**File:** `src/api/simple_backend.py:53`
**Module:** `src.api.simple_backend`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/project/services
- Add UI button/form calling GET /api/project/services in appropriate React component

### POST /api/project/delegate
**File:** `src/api/simple_backend.py:58`
**Module:** `src.api.simple_backend`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/project/delegate
- Add UI button/form calling POST /api/project/delegate in appropriate React component

### GET /api/project/stats
**File:** `src/api/simple_backend.py:102`
**Module:** `src.api.simple_backend`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/project/stats
- Add UI button/form calling GET /api/project/stats in appropriate React component

### GET /api/settings
**File:** `src/api/simple_backend.py:144`
**Module:** `src.api.simple_backend`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/settings
- Add UI button/form calling GET /api/settings in appropriate React component

### POST /api/settings
**File:** `src/api/simple_backend.py:149`
**Module:** `src.api.simple_backend`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/settings
- Add UI button/form calling POST /api/settings in appropriate React component

### GET /api/superclaude/sessions
**File:** `src/api/superclaude_api.py:422`
**Module:** `src.api.superclaude_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/superclaude/sessions
- Add UI button/form calling GET /api/superclaude/sessions in appropriate React component

### DELETE /api/superclaude/session/<session_id>
**File:** `src/api/superclaude_api.py:440`
**Module:** `src.api.superclaude_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting DELETE /api/superclaude/session/<session_id>
- Add UI button/form calling DELETE /api/superclaude/session/<session_id> in appropriate React component

### GET /api/superclaude/circuit-breakers/status
**File:** `src/api/superclaude_api.py:466`
**Module:** `src.api.superclaude_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/superclaude/circuit-breakers/status
- Add UI button/form calling GET /api/superclaude/circuit-breakers/status in appropriate React component

### POST /api/superclaude/circuit-breakers/<service_name>/reset
**File:** `src/api/superclaude_api.py:479`
**Module:** `src.api.superclaude_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/superclaude/circuit-breakers/<service_name>/reset
- Add UI button/form calling POST /api/superclaude/circuit-breakers/<service_name>/reset in appropriate React component

### GET /api/llm/health
**File:** `src/api/system_health.py:33`
**Module:** `src.api.system_health`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/llm/health
- Add UI button/form calling GET /api/llm/health in appropriate React component

### GET /api/synapse/health
**File:** `src/api/system_health.py:70`
**Module:** `src.api.system_health`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/health
- Add UI button/form calling GET /api/synapse/health in appropriate React component

### GET /api/core/health
**File:** `src/api/system_health.py:89`
**Module:** `src.api.system_health`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/core/health
- Add UI button/form calling GET /api/core/health in appropriate React component

### GET /api/sentry/health
**File:** `src/api/system_health.py:106`
**Module:** `src.api.system_health`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/sentry/health
- Add UI button/form calling GET /api/sentry/health in appropriate React component

### GET /api/system/memory
**File:** `src/api/system_health.py:123`
**Module:** `src.api.system_health`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/system/memory
- Add UI button/form calling GET /api/system/memory in appropriate React component

### GET /api/system/health
**File:** `src/api/system_health.py:144`
**Module:** `src.api.system_health`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/system/health
- Add UI button/form calling GET /api/system/health in appropriate React component

### GET /api/vault/stats
**File:** `src/api/system_health.py:203`
**Module:** `src.api.system_health`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/vault/stats
- Add UI button/form calling GET /api/vault/stats in appropriate React component

### GET /api/vault/memories
**File:** `src/api/system_health.py:223`
**Module:** `src.api.system_health`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/vault/memories
- Add UI button/form calling GET /api/vault/memories in appropriate React component

### GET /api/vault/audit-log
**File:** `src/api/system_health.py:265`
**Module:** `src.api.system_health`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/vault/audit-log
- Add UI button/form calling GET /api/vault/audit-log in appropriate React component

### POST /api/connect/llm
**File:** `src/api/system_health.py:304`
**Module:** `src.api.system_health`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/connect/llm
- Add UI button/form calling POST /api/connect/llm in appropriate React component

### POST /api/connect/vault
**File:** `src/api/system_health.py:318`
**Module:** `src.api.system_health`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/connect/vault
- Add UI button/form calling POST /api/connect/vault in appropriate React component

### POST /api/connect/synapse
**File:** `src/api/system_health.py:332`
**Module:** `src.api.system_health`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/connect/synapse
- Add UI button/form calling POST /api/connect/synapse in appropriate React component

### GET /{template_id}
**File:** `src/api/task_templates.py:248`
**Module:** `src.api.task_templates`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /{template_id}
- Add UI button/form calling GET /{template_id} in appropriate React component

### GET /{template_id}
**File:** `src/api/task_templates.py:319`
**Module:** `src.api.task_templates`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /{template_id}
- Add UI button/form calling GET /{template_id} in appropriate React component

### GET /{template_id}
**File:** `src/api/task_templates.py:366`
**Module:** `src.api.task_templates`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /{template_id}
- Add UI button/form calling GET /{template_id} in appropriate React component

### GET /audit/{entity_id}
**File:** `src/api/task_templates.py:423`
**Module:** `src.api.task_templates`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /audit/{entity_id}
- Add UI button/form calling GET /audit/{entity_id} in appropriate React component

### GET /api/vault/stats
**File:** `src/api/vault_api.py:83`
**Module:** `src.api.vault_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/vault/stats
- Add UI button/form calling GET /api/vault/stats in appropriate React component

### GET /api/vault/memories
**File:** `src/api/vault_api.py:111`
**Module:** `src.api.vault_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/vault/memories
- Add UI button/form calling GET /api/vault/memories in appropriate React component

### POST /api/vault/memories
**File:** `src/api/vault_api.py:155`
**Module:** `src.api.vault_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/vault/memories
- Add UI button/form calling POST /api/vault/memories in appropriate React component

### PUT /api/vault/memories/<memory_id>
**File:** `src/api/vault_api.py:209`
**Module:** `src.api.vault_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting PUT /api/vault/memories/<memory_id>
- Add UI button/form calling PUT /api/vault/memories/<memory_id> in appropriate React component

### DELETE /api/vault/memories/<memory_id>
**File:** `src/api/vault_api.py:238`
**Module:** `src.api.vault_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting DELETE /api/vault/memories/<memory_id>
- Add UI button/form calling DELETE /api/vault/memories/<memory_id> in appropriate React component

### GET /api/vault/audit-log
**File:** `src/api/vault_api.py:262`
**Module:** `src.api.vault_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/vault/audit-log
- Add UI button/form calling GET /api/vault/audit-log in appropriate React component

### POST /api/vault/backup
**File:** `src/api/vault_api.py:291`
**Module:** `src.api.vault_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/vault/backup
- Add UI button/form calling POST /api/vault/backup in appropriate React component

### GET /api/vault/integrity
**File:** `src/api/vault_api.py:311`
**Module:** `src.api.vault_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/vault/integrity
- Add UI button/form calling GET /api/vault/integrity in appropriate React component

### POST /api/vault/search
**File:** `src/api/vault_api.py:331`
**Module:** `src.api.vault_api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting POST /api/vault/search
- Add UI button/form calling POST /api/vault/search in appropriate React component

### GET /api/core/session
**File:** `src/core/api.py:113`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/session in appropriate React component

### GET /api/core/session/{session_id}
**File:** `src/core/api.py:136`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/session/{session_id} in appropriate React component

### GET /api/core/sessions
**File:** `src/core/api.py:156`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/sessions in appropriate React component

### GET /api/core/session/{session_id}/participants
**File:** `src/core/api.py:174`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/session/{session_id}/participants in appropriate React component

### GET /api/core/session/{session_id}/participants/{participant_id}
**File:** `src/core/api.py:194`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/session/{session_id}/participants/{participant_id} in appropriate React component

### GET /api/core/session/{session_id}/participants
**File:** `src/core/api.py:214`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/core/session/{session_id}/participants
- Add UI button/form calling GET /api/core/session/{session_id}/participants in appropriate React component

### GET /api/core/session/{session_id}/turn-taking/start
**File:** `src/core/api.py:240`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/session/{session_id}/turn-taking/start in appropriate React component

### GET /api/core/session/{session_id}/turn-taking/advance
**File:** `src/core/api.py:260`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/session/{session_id}/turn-taking/advance in appropriate React component

### GET /api/core/session/{session_id}/breakout
**File:** `src/core/api.py:289`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/session/{session_id}/breakout in appropriate React component

### GET /api/core/session/{session_id}/breakout/{breakout_id}
**File:** `src/core/api.py:309`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/session/{session_id}/breakout/{breakout_id} in appropriate React component

### GET /api/core/session/{session_id}/insights
**File:** `src/core/api.py:329`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/session/{session_id}/insights in appropriate React component

### GET /api/core/session/{session_id}/log
**File:** `src/core/api.py:351`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/session/{session_id}/log in appropriate React component

### GET /api/core/session/{session_id}/settings
**File:** `src/core/api.py:371`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/core/session/{session_id}/settings
- Add UI button/form calling GET /api/core/session/{session_id}/settings in appropriate React component

### GET /api/core/session/{session_id}/pause
**File:** `src/core/api.py:397`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/session/{session_id}/pause in appropriate React component

### GET /api/core/session/{session_id}/resume
**File:** `src/core/api.py:416`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/session/{session_id}/resume in appropriate React component

### GET /api/core/session/{session_id}
**File:** `src/core/api.py:435`
**Module:** `src.core.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/core/session/{session_id} in appropriate React component

### GET /api/synapse/plugin/register
**File:** `src/synapse/api.py:151`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/synapse/plugin/register in appropriate React component

### GET /api/synapse/plugin/{plugin_id}/approve
**File:** `src/synapse/api.py:173`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/synapse/plugin/{plugin_id}/approve in appropriate React component

### GET /api/synapse/plugin/{plugin_id}/revoke
**File:** `src/synapse/api.py:198`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/plugin/{plugin_id}/revoke
- Add UI button/form calling GET /api/synapse/plugin/{plugin_id}/revoke in appropriate React component

### GET /api/synapse/plugin/{plugin_id}/execute
**File:** `src/synapse/api.py:223`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/synapse/plugin/{plugin_id}/execute in appropriate React component

### GET /api/synapse/plugin/{plugin_id}/status
**File:** `src/synapse/api.py:254`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/plugin/{plugin_id}/status
- Add UI button/form calling GET /api/synapse/plugin/{plugin_id}/status in appropriate React component

### GET /api/synapse/plugins
**File:** `src/synapse/api.py:275`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/plugins
- Add UI button/form calling GET /api/synapse/plugins in appropriate React component

### GET /api/synapse/plugin/{plugin_id}/permissions/request
**File:** `src/synapse/api.py:295`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/plugin/{plugin_id}/permissions/request
- Add UI button/form calling GET /api/synapse/plugin/{plugin_id}/permissions/request in appropriate React component

### GET /api/synapse/permissions/{request_id}/approve
**File:** `src/synapse/api.py:317`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/permissions/{request_id}/approve
- Add UI button/form calling GET /api/synapse/permissions/{request_id}/approve in appropriate React component

### GET /api/synapse/permissions/{request_id}/deny
**File:** `src/synapse/api.py:340`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/permissions/{request_id}/deny
- Add UI button/form calling GET /api/synapse/permissions/{request_id}/deny in appropriate React component

### GET /api/synapse/permissions/pending
**File:** `src/synapse/api.py:363`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/permissions/pending
- Add UI button/form calling GET /api/synapse/permissions/pending in appropriate React component

### GET /api/synapse/connection/request
**File:** `src/synapse/api.py:382`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/synapse/connection/request in appropriate React component

### GET /api/synapse/connection/{connection_id}/approve
**File:** `src/synapse/api.py:403`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/synapse/connection/{connection_id}/approve in appropriate React component

### GET /api/synapse/connection/{connection_id}/close
**File:** `src/synapse/api.py:422`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/synapse/connection/{connection_id}/close in appropriate React component

### GET /api/synapse/connections
**File:** `src/synapse/api.py:444`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/connections
- Add UI button/form calling GET /api/synapse/connections in appropriate React component

### GET /api/synapse/webhooks
**File:** `src/synapse/api.py:462`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/webhooks
- Add UI button/form calling GET /api/synapse/webhooks in appropriate React component

### GET /api/synapse/webhooks
**File:** `src/synapse/api.py:488`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/webhooks
- Add UI button/form calling GET /api/synapse/webhooks in appropriate React component

### GET /api/synapse/plugin/{plugin_id}/benchmark
**File:** `src/synapse/api.py:514`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/plugin/{plugin_id}/benchmark
- Add UI button/form calling GET /api/synapse/plugin/{plugin_id}/benchmark in appropriate React component

### GET /api/synapse/plugin/{plugin_id}/benchmark
**File:** `src/synapse/api.py:542`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/plugin/{plugin_id}/benchmark
- Add UI button/form calling GET /api/synapse/plugin/{plugin_id}/benchmark in appropriate React component

### GET /api/synapse/traffic/logs
**File:** `src/synapse/api.py:569`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/traffic/logs
- Add UI button/form calling GET /api/synapse/traffic/logs in appropriate React component

### GET /api/synapse/traffic/summary
**File:** `src/synapse/api.py:587`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/traffic/summary
- Add UI button/form calling GET /api/synapse/traffic/summary in appropriate React component

### GET /api/synapse/traffic/export
**File:** `src/synapse/api.py:605`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/traffic/export
- Add UI button/form calling GET /api/synapse/traffic/export in appropriate React component

### GET /api/synapse/system/status
**File:** `src/synapse/api.py:629`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/synapse/system/status in appropriate React component

### GET /api/synapse/system/export
**File:** `src/synapse/api.py:646`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/system/export
- Add UI button/form calling GET /api/synapse/system/export in appropriate React component

### GET /api/synapse/system/cleanup
**File:** `src/synapse/api.py:663`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/synapse/system/cleanup in appropriate React component

### GET /api/settings
**File:** `src/synapse/api.py:686`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/settings
- Add UI button/form calling GET /api/settings in appropriate React component

### GET /api/settings
**File:** `src/synapse/api.py:712`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/settings
- Add UI button/form calling GET /api/settings in appropriate React component

### GET /api/synapse/health
**File:** `src/synapse/api.py:745`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/synapse/health in appropriate React component

### GET /api/synapse/handoff/{source_agent_id}/initiate
**File:** `src/synapse/api.py:756`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/synapse/handoff/{source_agent_id}/initiate in appropriate React component

### GET /api/synapse/handoff/{handoff_id}/status
**File:** `src/synapse/api.py:796`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/synapse/handoff/{handoff_id}/status in appropriate React component

### GET /api/synapse/handoff/{handoff_id}/cancel
**File:** `src/synapse/api.py:828`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/handoff/{handoff_id}/cancel
- Add UI button/form calling GET /api/synapse/handoff/{handoff_id}/cancel in appropriate React component

### GET /api/synapse/handoffs/active
**File:** `src/synapse/api.py:850`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/handoffs/active
- Add UI button/form calling GET /api/synapse/handoffs/active in appropriate React component

### GET /api/synapse/handoffs/history
**File:** `src/synapse/api.py:867`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/handoffs/history
- Add UI button/form calling GET /api/synapse/handoffs/history in appropriate React component

### GET /api/synapse/agents/capabilities
**File:** `src/synapse/api.py:885`
**Module:** `src.synapse.api`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/synapse/agents/capabilities
- Add UI button/form calling GET /api/synapse/agents/capabilities in appropriate React component

### GET /api/health
**File:** `src/synapse/claude_gateway.py:205`
**Module:** `src.synapse.claude_gateway`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/health in appropriate React component

### GET /api/claude/validate
**File:** `src/synapse/claude_gateway.py:218`
**Module:** `src.synapse.claude_gateway`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/claude/validate
- Add UI button/form calling GET /api/claude/validate in appropriate React component

### GET /api/vault/append
**File:** `src/synapse/claude_gateway.py:294`
**Module:** `src.synapse.claude_gateway`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /api/vault/append
- Add UI button/form calling GET /api/vault/append in appropriate React component

### GET /directives
**File:** `src/synapse/claude_gateway.py:354`
**Module:** `src.synapse.claude_gateway`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /directives
- Add UI button/form calling GET /directives in appropriate React component

### GET /servers
**File:** `src/synapse/api/mcp_endpoints.py:56`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /servers in appropriate React component

### GET /servers/{server_id}
**File:** `src/synapse/api/mcp_endpoints.py:86`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /servers/{server_id}
- Add UI button/form calling GET /servers/{server_id} in appropriate React component

### GET /servers/{server_id}/start
**File:** `src/synapse/api/mcp_endpoints.py:119`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /servers/{server_id}/start
- Add UI button/form calling GET /servers/{server_id}/start in appropriate React component

### GET /servers/{server_id}/stop
**File:** `src/synapse/api/mcp_endpoints.py:140`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /servers/{server_id}/stop
- Add UI button/form calling GET /servers/{server_id}/stop in appropriate React component

### GET /servers/{server_id}/tools
**File:** `src/synapse/api/mcp_endpoints.py:161`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /servers/{server_id}/tools
- Add UI button/form calling GET /servers/{server_id}/tools in appropriate React component

### GET /servers/{server_id}/execute
**File:** `src/synapse/api/mcp_endpoints.py:188`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /servers/{server_id}/execute
- Add UI button/form calling GET /servers/{server_id}/execute in appropriate React component

### GET /servers/{server_id}/health
**File:** `src/synapse/api/mcp_endpoints.py:216`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /servers/{server_id}/health
- Add UI button/form calling GET /servers/{server_id}/health in appropriate React component

### GET /health
**File:** `src/synapse/api/mcp_endpoints.py:246`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /health in appropriate React component

### GET /gmail/send
**File:** `src/synapse/api/mcp_endpoints.py:271`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /gmail/send
- Add UI button/form calling GET /gmail/send in appropriate React component

### GET /gmail/emails
**File:** `src/synapse/api/mcp_endpoints.py:304`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /gmail/emails
- Add UI button/form calling GET /gmail/emails in appropriate React component

### GET /calendar/events
**File:** `src/synapse/api/mcp_endpoints.py:333`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /calendar/events
- Add UI button/form calling GET /calendar/events in appropriate React component

### GET /calendar/events
**File:** `src/synapse/api/mcp_endpoints.py:366`
**Module:** `src.synapse.api.mcp_endpoints`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting GET /calendar/events
- Add UI button/form calling GET /calendar/events in appropriate React component

### IPC /ipc/core-create-session
**File:** `ipcHandlers/core.ts:17`
**Module:** `ipcHandlers.core`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/core-create-session
- Add UI button/form calling IPC /ipc/core-create-session in appropriate React component

### IPC /ipc/core-get-session
**File:** `ipcHandlers/core.ts:33`
**Module:** `ipcHandlers.core`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/core-get-session
- Add UI button/form calling IPC /ipc/core-get-session in appropriate React component

### IPC /ipc/core-add-participant
**File:** `ipcHandlers/core.ts:49`
**Module:** `ipcHandlers.core`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/core-add-participant
- Add UI button/form calling IPC /ipc/core-add-participant in appropriate React component

### IPC /ipc/core-start-turn-taking
**File:** `ipcHandlers/core.ts:65`
**Module:** `ipcHandlers.core`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/core-start-turn-taking
- Add UI button/form calling IPC /ipc/core-start-turn-taking in appropriate React component

### IPC /ipc/core-advance-turn
**File:** `ipcHandlers/core.ts:81`
**Module:** `ipcHandlers.core`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/core-advance-turn
- Add UI button/form calling IPC /ipc/core-advance-turn in appropriate React component

### IPC /ipc/get-app-version
**File:** `ipcHandlers/general.ts:7`
**Module:** `ipcHandlers.general`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling IPC /ipc/get-app-version in appropriate React component

### IPC /ipc/get-app-path
**File:** `ipcHandlers/general.ts:11`
**Module:** `ipcHandlers.general`
**Type:** endpoint
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling IPC /ipc/get-app-path in appropriate React component

### IPC /ipc/get-resource-path
**File:** `ipcHandlers/general.ts:15`
**Module:** `ipcHandlers.general`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/get-resource-path
- Add UI button/form calling IPC /ipc/get-resource-path in appropriate React component

### IPC /ipc/read-documentation
**File:** `ipcHandlers/general.ts:19`
**Module:** `ipcHandlers.general`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/read-documentation
- Add UI button/form calling IPC /ipc/read-documentation in appropriate React component

### IPC /ipc/open-external
**File:** `ipcHandlers/general.ts:29`
**Module:** `ipcHandlers.general`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/open-external
- Add UI button/form calling IPC /ipc/open-external in appropriate React component

### IPC /ipc/voice-command
**File:** `ipcHandlers/general.ts:38`
**Module:** `ipcHandlers.general`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/voice-command
- Add UI button/form calling IPC /ipc/voice-command in appropriate React component

### IPC /ipc/accessibility-toggle
**File:** `ipcHandlers/general.ts:77`
**Module:** `ipcHandlers.general`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/accessibility-toggle
- Add UI button/form calling IPC /ipc/accessibility-toggle in appropriate React component

### IPC /ipc/synapse-execute-plugin
**File:** `ipcHandlers/synapse.ts:17`
**Module:** `ipcHandlers.synapse`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/synapse-execute-plugin
- Add UI button/form calling IPC /ipc/synapse-execute-plugin in appropriate React component

### IPC /ipc/synapse-list-plugins
**File:** `ipcHandlers/synapse.ts:33`
**Module:** `ipcHandlers.synapse`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/synapse-list-plugins
- Add UI button/form calling IPC /ipc/synapse-list-plugins in appropriate React component

### IPC /ipc/vault-get-persona-memory
**File:** `ipcHandlers/vault.ts:17`
**Module:** `ipcHandlers.vault`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/vault-get-persona-memory
- Add UI button/form calling IPC /ipc/vault-get-persona-memory in appropriate React component

### IPC /ipc/vault-update-persona-memory
**File:** `ipcHandlers/vault.ts:33`
**Module:** `ipcHandlers.vault`
**Type:** endpoint
**Missing:** test, ui_invocation

**Recommendations:**
- Add Playwright test in tests/e2e/ hitting IPC /ipc/vault-update-persona-memory
- Add UI button/form calling IPC /ipc/vault-update-persona-memory in appropriate React component

## High Priority Gaps

### init_database
**File:** `src/api_server.py:37`
**Module:** `src.api_server`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for init_database
- Consider adding UI control for init_database if user-facing
- Consider adding CLI command for init_database if appropriate

### list_agents
**File:** `src/api_server.py:140`
**Module:** `src.api_server`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_agents
- Consider adding UI control for list_agents if user-facing
- Consider adding CLI command for list_agents if appropriate

### get_agent
**File:** `src/api_server.py:169`
**Module:** `src.api_server`
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for get_agent if user-facing

### list_tokens
**File:** `src/api_server.py:252`
**Module:** `src.api_server`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_tokens
- Consider adding UI control for list_tokens if user-facing
- Consider adding CLI command for list_tokens if appropriate

### verify_token
**File:** `src/api_server.py:288`
**Module:** `src.api_server`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for verify_token
- Consider adding UI control for verify_token if user-facing
- Consider adding CLI command for verify_token if appropriate

### log_startup
**File:** `src/main.py:231`
**Module:** `src.main`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for log_startup if user-facing
- Consider adding CLI command for log_startup if appropriate

### log_shutdown
**File:** `src/main.py:268`
**Module:** `src.main`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for log_shutdown if user-facing
- Consider adding CLI command for log_shutdown if appropriate

### log_error
**File:** `src/main.py:288`
**Module:** `src.main`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for log_error if user-facing
- Consider adding CLI command for log_error if appropriate

### log_critical_error
**File:** `src/main.py:316`
**Module:** `src.main`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for log_critical_error if user-facing
- Consider adding CLI command for log_critical_error if appropriate

### simulate_error
**File:** `src/main.py:635`
**Module:** `src.main`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for simulate_error if user-facing
- Consider adding CLI command for simulate_error if appropriate

### signal_handler
**File:** `src/main.py:402`
**Module:** `src.main`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for signal_handler
- Consider adding UI control for signal_handler if user-facing
- Consider adding CLI command for signal_handler if appropriate

### load_config
**File:** `src/run_alden.py:32`
**Module:** `src.run_alden`
**Missing:** test, ui_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for load_config
- Consider adding UI control for load_config if user-facing

### start_services
**File:** `src/run_services.py:38`
**Module:** `src.run_services`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_services
- Consider adding UI control for start_services if user-facing
- Consider adding CLI command for start_services if appropriate

### signal_handler
**File:** `src/run_services.py:130`
**Module:** `src.run_services`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for signal_handler
- Consider adding UI control for signal_handler if user-facing
- Consider adding CLI command for signal_handler if appropriate

### validate_message
**File:** `src/api/alden_api.py:52`
**Module:** `src.api.alden_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_message
- Consider adding UI control for validate_message if user-facing
- Consider adding CLI command for validate_message if appropriate

### send_message
**File:** `src/api/alden_api.py:162`
**Module:** `src.api.alden_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for send_message
- Consider adding UI control for send_message if user-facing
- Consider adding CLI command for send_message if appropriate

### add_correction
**File:** `src/api/alden_api.py:230`
**Module:** `src.api.alden_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for add_correction
- Consider adding UI control for add_correction if user-facing
- Consider adding CLI command for add_correction if appropriate

### record_mood
**File:** `src/api/alden_api.py:259`
**Module:** `src.api.alden_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for record_mood
- Consider adding UI control for record_mood if user-facing
- Consider adding CLI command for record_mood if appropriate

### export_memory
**File:** `src/api/alden_api.py:309`
**Module:** `src.api.alden_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_memory
- Consider adding UI control for export_memory if user-facing
- Consider adding CLI command for export_memory if appropriate

### initialize_claude_code_cli
**File:** `src/api/claude_code_cli.py:318`
**Module:** `src.api.claude_code_cli`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for initialize_claude_code_cli
- Consider adding UI control for initialize_claude_code_cli if user-facing
- Consider adding CLI command for initialize_claude_code_cli if appropriate

### is_available
**File:** `src/api/claude_code_cli.py:44`
**Module:** `src.api.claude_code_cli`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for is_available
- Consider adding UI control for is_available if user-facing
- Consider adding CLI command for is_available if appropriate

### start_session
**File:** `src/api/claude_code_cli.py:79`
**Module:** `src.api.claude_code_cli`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_session
- Consider adding UI control for start_session if user-facing
- Consider adding CLI command for start_session if appropriate

### analyze_code
**File:** `src/api/claude_code_cli.py:163`
**Module:** `src.api.claude_code_cli`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for analyze_code
- Consider adding UI control for analyze_code if user-facing
- Consider adding CLI command for analyze_code if appropriate

### generate_code
**File:** `src/api/claude_code_cli.py:174`
**Module:** `src.api.claude_code_cli`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_code
- Consider adding UI control for generate_code if user-facing
- Consider adding CLI command for generate_code if appropriate

### refactor_code
**File:** `src/api/claude_code_cli.py:191`
**Module:** `src.api.claude_code_cli`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for refactor_code
- Consider adding UI control for refactor_code if user-facing
- Consider adding CLI command for refactor_code if appropriate

### explain_code
**File:** `src/api/claude_code_cli.py:206`
**Module:** `src.api.claude_code_cli`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for explain_code
- Consider adding UI control for explain_code if user-facing
- Consider adding CLI command for explain_code if appropriate

### debug_code
**File:** `src/api/claude_code_cli.py:220`
**Module:** `src.api.claude_code_cli`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for debug_code
- Consider adding UI control for debug_code if user-facing
- Consider adding CLI command for debug_code if appropriate

### end_session
**File:** `src/api/claude_code_cli.py:242`
**Module:** `src.api.claude_code_cli`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for end_session if user-facing
- Consider adding CLI command for end_session if appropriate

### initialize_mock_data
**File:** `src/api/core_api.py:100`
**Module:** `src.api.core_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for initialize_mock_data
- Consider adding UI control for initialize_mock_data if user-facing
- Consider adding CLI command for initialize_mock_data if appropriate

### add_orchestration_log
**File:** `src/api/core_api.py:254`
**Module:** `src.api.core_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for add_orchestration_log
- Consider adding UI control for add_orchestration_log if user-facing
- Consider adding CLI command for add_orchestration_log if appropriate

### get_agent
**File:** `src/api/core_api.py:301`
**Module:** `src.api.core_api`
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for get_agent if user-facing

### check_service_health
**File:** `src/api/core_api.py:334`
**Module:** `src.api.core_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_service_health
- Consider adding UI control for check_service_health if user-facing
- Consider adding CLI command for check_service_health if appropriate

### start_project_orchestration
**File:** `src/api/core_api.py:399`
**Module:** `src.api.core_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_project_orchestration
- Consider adding UI control for start_project_orchestration if user-facing
- Consider adding CLI command for start_project_orchestration if appropriate

### delegate_task
**File:** `src/api/core_api.py:422`
**Module:** `src.api.core_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for delegate_task
- Consider adding UI control for delegate_task if user-facing
- Consider adding CLI command for delegate_task if appropriate

### create_session
**File:** `src/api/core_api.py:453`
**Module:** `src.api.core_api`
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for create_session if user-facing

### get_session
**File:** `src/api/core_api.py:479`
**Module:** `src.api.core_api`
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for get_session if user-facing

### join_session
**File:** `src/api/core_api.py:487`
**Module:** `src.api.core_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for join_session
- Consider adding UI control for join_session if user-facing
- Consider adding CLI command for join_session if appropriate

### send_session_message
**File:** `src/api/core_api.py:511`
**Module:** `src.api.core_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for send_session_message
- Consider adding UI control for send_session_message if user-facing
- Consider adding CLI command for send_session_message if appropriate

### authenticate_request
**File:** `src/api/enhanced_core_api.py:77`
**Module:** `src.api.enhanced_core_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for authenticate_request
- Consider adding UI control for authenticate_request if user-facing
- Consider adding CLI command for authenticate_request if appropriate

### delegate_task
**File:** `src/api/enhanced_core_api.py:146`
**Module:** `src.api.enhanced_core_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for delegate_task
- Consider adding UI control for delegate_task if user-facing
- Consider adding CLI command for delegate_task if appropriate

### control_workflow
**File:** `src/api/enhanced_core_api.py:216`
**Module:** `src.api.enhanced_core_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for control_workflow
- Consider adding UI control for control_workflow if user-facing
- Consider adding CLI command for control_workflow if appropriate

### suggest_agent
**File:** `src/api/enhanced_core_api.py:329`
**Module:** `src.api.enhanced_core_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for suggest_agent
- Consider adding UI control for suggest_agent if user-facing
- Consider adding CLI command for suggest_agent if appropriate

### startup_event
**File:** `src/api/enhanced_core_api.py:397`
**Module:** `src.api.enhanced_core_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for startup_event if user-facing
- Consider adding CLI command for startup_event if appropriate

### shutdown_event
**File:** `src/api/enhanced_core_api.py:429`
**Module:** `src.api.enhanced_core_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for shutdown_event if user-facing
- Consider adding CLI command for shutdown_event if appropriate

### list_external_agents
**File:** `src/api/external_agent_api.py:162`
**Module:** `src.api.external_agent_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_external_agents
- Consider adding UI control for list_external_agents if user-facing
- Consider adding CLI command for list_external_agents if appropriate

### generate_with_agent
**File:** `src/api/external_agent_api.py:263`
**Module:** `src.api.external_agent_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_with_agent
- Consider adding UI control for generate_with_agent if user-facing
- Consider adding CLI command for generate_with_agent if appropriate

### write_file_with_agent
**File:** `src/api/external_agent_api.py:309`
**Module:** `src.api.external_agent_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for write_file_with_agent
- Consider adding UI control for write_file_with_agent if user-facing
- Consider adding CLI command for write_file_with_agent if appropriate

### read_file_with_agent
**File:** `src/api/external_agent_api.py:355`
**Module:** `src.api.external_agent_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for read_file_with_agent
- Consider adding UI control for read_file_with_agent if user-facing
- Consider adding CLI command for read_file_with_agent if appropriate

### list_files_with_agent
**File:** `src/api/external_agent_api.py:399`
**Module:** `src.api.external_agent_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_files_with_agent
- Consider adding UI control for list_files_with_agent if user-facing
- Consider adding CLI command for list_files_with_agent if appropriate

### reset_circuit_breaker
**File:** `src/api/external_agent_api.py:450`
**Module:** `src.api.external_agent_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for reset_circuit_breaker
- Consider adding UI control for reset_circuit_breaker if user-facing
- Consider adding CLI command for reset_circuit_breaker if appropriate

### reset_all_circuit_breakers
**File:** `src/api/external_agent_api.py:475`
**Module:** `src.api.external_agent_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for reset_all_circuit_breakers
- Consider adding UI control for reset_all_circuit_breakers if user-facing
- Consider adding CLI command for reset_all_circuit_breakers if appropriate

### check_rate_limit
**File:** `src/api/kimi_k2_api.py:84`
**Module:** `src.api.kimi_k2_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_rate_limit
- Consider adding UI control for check_rate_limit if user-facing
- Consider adding CLI command for check_rate_limit if appropriate

### authenticate_request
**File:** `src/api/kimi_k2_api.py:94`
**Module:** `src.api.kimi_k2_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for authenticate_request
- Consider adding UI control for authenticate_request if user-facing
- Consider adding CLI command for authenticate_request if appropriate

### chat
**File:** `src/api/kimi_k2_api.py:107`
**Module:** `src.api.kimi_k2_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for chat if user-facing
- Consider adding CLI command for chat if appropriate

### agentic_workflow
**File:** `src/api/kimi_k2_api.py:204`
**Module:** `src.api.kimi_k2_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for agentic_workflow
- Consider adding UI control for agentic_workflow if user-facing
- Consider adding CLI command for agentic_workflow if appropriate

### long_context_processing
**File:** `src/api/kimi_k2_api.py:247`
**Module:** `src.api.kimi_k2_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for long_context_processing
- Consider adding UI control for long_context_processing if user-facing
- Add CLI command wrapper for long_context_processing

### estimate_cost
**File:** `src/api/kimi_k2_api.py:365`
**Module:** `src.api.kimi_k2_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for estimate_cost
- Consider adding UI control for estimate_cost if user-facing
- Consider adding CLI command for estimate_cost if appropriate

### startup_event
**File:** `src/api/kimi_k2_api.py:422`
**Module:** `src.api.kimi_k2_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for startup_event if user-facing
- Consider adding CLI command for startup_event if appropriate

### shutdown_event
**File:** `src/api/kimi_k2_api.py:434`
**Module:** `src.api.kimi_k2_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for shutdown_event if user-facing
- Consider adding CLI command for shutdown_event if appropriate

### generate_license_hash
**File:** `src/api/license_validation.py:86`
**Module:** `src.api.license_validation`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_license_hash
- Consider adding UI control for generate_license_hash if user-facing
- Consider adding CLI command for generate_license_hash if appropriate

### validate_license_format
**File:** `src/api/license_validation.py:91`
**Module:** `src.api.license_validation`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_license_format
- Consider adding UI control for validate_license_format if user-facing
- Consider adding CLI command for validate_license_format if appropriate

### validate_steve_august_license
**File:** `src/api/license_validation.py:141`
**Module:** `src.api.license_validation`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_steve_august_license
- Consider adding UI control for validate_steve_august_license if user-facing
- Consider adding CLI command for validate_steve_august_license if appropriate

### validate_template_license
**File:** `src/api/license_validation.py:170`
**Module:** `src.api.license_validation`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_template_license
- Consider adding UI control for validate_template_license if user-facing
- Consider adding CLI command for validate_template_license if appropriate

### record_template_usage
**File:** `src/api/license_validation.py:240`
**Module:** `src.api.license_validation`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for record_template_usage
- Consider adding UI control for record_template_usage if user-facing
- Consider adding CLI command for record_template_usage if appropriate

### start_template_trial
**File:** `src/api/license_validation.py:276`
**Module:** `src.api.license_validation`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_template_trial
- Consider adding UI control for start_template_trial if user-facing
- Consider adding CLI command for start_template_trial if appropriate

### initialize_llm_services
**File:** `src/api/llm_connector.py:89`
**Module:** `src.api.llm_connector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for initialize_llm_services
- Consider adding UI control for initialize_llm_services if user-facing
- Consider adding CLI command for initialize_llm_services if appropriate

### check_ollama_connection
**File:** `src/api/llm_connector.py:18`
**Module:** `src.api.llm_connector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_ollama_connection
- Consider adding UI control for check_ollama_connection if user-facing
- Consider adding CLI command for check_ollama_connection if appropriate

### install_model
**File:** `src/api/llm_connector.py:33`
**Module:** `src.api.llm_connector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for install_model
- Consider adding UI control for install_model if user-facing
- Consider adding CLI command for install_model if appropriate

### generate_response
**File:** `src/api/llm_connector.py:59`
**Module:** `src.api.llm_connector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_response
- Consider adding UI control for generate_response if user-facing
- Consider adding CLI command for generate_response if appropriate

### check_ollama_connection
**File:** `src/api/local_llm_api.py:180`
**Module:** `src.api.local_llm_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_ollama_connection
- Consider adding UI control for check_ollama_connection if user-facing
- Consider adding CLI command for check_ollama_connection if appropriate

### select_model_for_task
**File:** `src/api/local_llm_api.py:232`
**Module:** `src.api.local_llm_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for select_model_for_task
- Consider adding UI control for select_model_for_task if user-facing
- Consider adding CLI command for select_model_for_task if appropriate

### pull_model
**File:** `src/api/local_llm_api.py:309`
**Module:** `src.api.local_llm_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for pull_model
- Consider adding UI control for pull_model if user-facing
- Consider adding CLI command for pull_model if appropriate

### chat
**File:** `src/api/local_llm_api.py:365`
**Module:** `src.api.local_llm_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for chat if user-facing
- Consider adding CLI command for chat if appropriate

### repair_websocket
**File:** `src/api/local_llm_api.py:796`
**Module:** `src.api.local_llm_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for repair_websocket
- Consider adding UI control for repair_websocket if user-facing
- Consider adding CLI command for repair_websocket if appropriate

### download_offline_model
**File:** `src/api/local_llm_api.py:840`
**Module:** `src.api.local_llm_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for download_offline_model
- Consider adding UI control for download_offline_model if user-facing
- Consider adding CLI command for download_offline_model if appropriate

### generate_offline
**File:** `src/api/local_llm_api.py:885`
**Module:** `src.api.local_llm_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_offline
- Consider adding UI control for generate_offline if user-facing
- Consider adding CLI command for generate_offline if appropriate

### activate_emergency_mode
**File:** `src/api/local_llm_api.py:972`
**Module:** `src.api.local_llm_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for activate_emergency_mode
- Consider adding UI control for activate_emergency_mode if user-facing
- Consider adding CLI command for activate_emergency_mode if appropriate

### reset_circuit_breaker
**File:** `src/api/local_llm_api.py:1007`
**Module:** `src.api.local_llm_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for reset_circuit_breaker
- Consider adding UI control for reset_circuit_breaker if user-facing
- Consider adding CLI command for reset_circuit_breaker if appropriate

### reset_all_circuit_breakers
**File:** `src/api/local_llm_api.py:1032`
**Module:** `src.api.local_llm_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for reset_all_circuit_breakers
- Consider adding UI control for reset_all_circuit_breakers if user-facing
- Consider adding CLI command for reset_all_circuit_breakers if appropriate

### save_settings
**File:** `src/api/local_llm_api.py:1051`
**Module:** `src.api.local_llm_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for save_settings
- Consider adding UI control for save_settings if user-facing
- Consider adding CLI command for save_settings if appropriate

### make_request
**File:** `src/api/local_llm_api.py:117`
**Module:** `src.api.local_llm_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for make_request if user-facing
- Consider adding CLI command for make_request if appropriate

### generate_persona
**File:** `src/api/mimic_api.py:202`
**Module:** `src.api.mimic_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for generate_persona if user-facing
- Consider adding CLI command for generate_persona if appropriate

### record_performance
**File:** `src/api/mimic_api.py:250`
**Module:** `src.api.mimic_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for record_performance if user-facing
- Consider adding CLI command for record_performance if appropriate

### fork_persona
**File:** `src/api/mimic_api.py:320`
**Module:** `src.api.mimic_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for fork_persona if user-facing
- Consider adding CLI command for fork_persona if appropriate

### merge_personas
**File:** `src/api/mimic_api.py:370`
**Module:** `src.api.mimic_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for merge_personas if user-facing
- Consider adding CLI command for merge_personas if appropriate

### add_plugin_extension
**File:** `src/api/mimic_api.py:411`
**Module:** `src.api.mimic_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for add_plugin_extension if user-facing
- Consider adding CLI command for add_plugin_extension if appropriate

### add_knowledge
**File:** `src/api/mimic_api.py:475`
**Module:** `src.api.mimic_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for add_knowledge
- Consider adding UI control for add_knowledge if user-facing
- Consider adding CLI command for add_knowledge if appropriate

### export_persona_memory
**File:** `src/api/mimic_api.py:590`
**Module:** `src.api.mimic_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_persona_memory
- Consider adding UI control for export_persona_memory if user-facing
- Consider adding CLI command for export_persona_memory if appropriate

### import_persona_memory
**File:** `src/api/mimic_api.py:615`
**Module:** `src.api.mimic_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for import_persona_memory
- Consider adding UI control for import_persona_memory if user-facing
- Consider adding CLI command for import_persona_memory if appropriate

### list_personas
**File:** `src/api/mimic_api.py:642`
**Module:** `src.api.mimic_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_personas
- Consider adding UI control for list_personas if user-facing
- Consider adding CLI command for list_personas if appropriate

### mimic_error_handler
**File:** `src/api/mimic_api.py:712`
**Module:** `src.api.mimic_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for mimic_error_handler
- Consider adding UI control for mimic_error_handler if user-facing
- Consider adding CLI command for mimic_error_handler if appropriate

### http_error_handler
**File:** `src/api/mimic_api.py:718`
**Module:** `src.api.mimic_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for http_error_handler
- Consider adding UI control for http_error_handler if user-facing
- Consider adding CLI command for http_error_handler if appropriate

### generate_response
**File:** `src/api/offline_llm_manager.py:406`
**Module:** `src.api.offline_llm_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_response
- Consider adding UI control for generate_response if user-facing
- Consider adding CLI command for generate_response if appropriate

### health_monitor
**File:** `src/api/offline_llm_manager.py:207`
**Module:** `src.api.offline_llm_manager`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for health_monitor if user-facing
- Consider adding CLI command for health_monitor if appropriate

### connection_monitor
**File:** `src/api/offline_llm_manager.py:212`
**Module:** `src.api.offline_llm_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for connection_monitor
- Consider adding UI control for connection_monitor if user-facing
- Consider adding CLI command for connection_monitor if appropriate

### add_monitoring_event
**File:** `src/api/sentry_api.py:49`
**Module:** `src.api.sentry_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for add_monitoring_event
- Consider adding UI control for add_monitoring_event if user-facing
- Consider adding CLI command for add_monitoring_event if appropriate

### add_alert
**File:** `src/api/sentry_api.py:66`
**Module:** `src.api.sentry_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for add_alert if user-facing
- Consider adding CLI command for add_alert if appropriate

### check_service_health
**File:** `src/api/sentry_api.py:86`
**Module:** `src.api.sentry_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_service_health
- Consider adding UI control for check_service_health if user-facing
- Consider adding CLI command for check_service_health if appropriate

### monitoring_loop
**File:** `src/api/sentry_api.py:361`
**Module:** `src.api.sentry_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for monitoring_loop
- Consider adding UI control for monitoring_loop if user-facing
- Consider adding CLI command for monitoring_loop if appropriate

### start_monitoring
**File:** `src/api/sentry_api.py:376`
**Module:** `src.api.sentry_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_monitoring
- Consider adding UI control for start_monitoring if user-facing
- Consider adding CLI command for start_monitoring if appropriate

### stop_monitoring_service
**File:** `src/api/sentry_api.py:389`
**Module:** `src.api.sentry_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for stop_monitoring_service
- Consider adding UI control for stop_monitoring_service if user-facing
- Consider adding CLI command for stop_monitoring_service if appropriate

### acknowledge_alert
**File:** `src/api/sentry_api.py:439`
**Module:** `src.api.sentry_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for acknowledge_alert
- Consider adding UI control for acknowledge_alert if user-facing
- Consider adding CLI command for acknowledge_alert if appropriate

### resolve_alert
**File:** `src/api/sentry_api.py:450`
**Module:** `src.api.sentry_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for resolve_alert
- Consider adding UI control for resolve_alert if user-facing
- Consider adding CLI command for resolve_alert if appropriate

### load_settings
**File:** `src/api/settings_api.py:103`
**Module:** `src.api.settings_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for load_settings
- Consider adding UI control for load_settings if user-facing
- Consider adding CLI command for load_settings if appropriate

### save_settings
**File:** `src/api/settings_api.py:122`
**Module:** `src.api.settings_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for save_settings
- Consider adding UI control for save_settings if user-facing
- Consider adding CLI command for save_settings if appropriate

### check_ollama_connection
**File:** `src/api/simple_backend.py:25`
**Module:** `src.api.simple_backend`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_ollama_connection
- Consider adding UI control for check_ollama_connection if user-facing
- Consider adding CLI command for check_ollama_connection if appropriate

### generate_ollama_response
**File:** `src/api/simple_backend.py:36`
**Module:** `src.api.simple_backend`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_ollama_response
- Consider adding UI control for generate_ollama_response if user-facing
- Consider adding CLI command for generate_ollama_response if appropriate

### delegate_task
**File:** `src/api/simple_backend.py:58`
**Module:** `src.api.simple_backend`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for delegate_task
- Consider adding UI control for delegate_task if user-facing
- Consider adding CLI command for delegate_task if appropriate

### save_settings
**File:** `src/api/simple_backend.py:149`
**Module:** `src.api.simple_backend`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for save_settings
- Consider adding UI control for save_settings if user-facing
- Consider adding CLI command for save_settings if appropriate

### check_backend_availability
**File:** `src/api/superclaude_api.py:248`
**Module:** `src.api.superclaude_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_backend_availability
- Consider adding UI control for check_backend_availability if user-facing
- Consider adding CLI command for check_backend_availability if appropriate

### create_session
**File:** `src/api/superclaude_api.py:290`
**Module:** `src.api.superclaude_api`
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for create_session if user-facing

### chat
**File:** `src/api/superclaude_api.py:335`
**Module:** `src.api.superclaude_api`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for chat if user-facing
- Consider adding CLI command for chat if appropriate

### list_sessions
**File:** `src/api/superclaude_api.py:422`
**Module:** `src.api.superclaude_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_sessions
- Consider adding UI control for list_sessions if user-facing
- Consider adding CLI command for list_sessions if appropriate

### reset_circuit_breaker
**File:** `src/api/superclaude_api.py:479`
**Module:** `src.api.superclaude_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for reset_circuit_breaker
- Consider adding UI control for reset_circuit_breaker if user-facing
- Consider adding CLI command for reset_circuit_breaker if appropriate

### add_message
**File:** `src/api/superclaude_api.py:94`
**Module:** `src.api.superclaude_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for add_message
- Consider adding UI control for add_message if user-facing
- Consider adding CLI command for add_message if appropriate

### enhance_prompt
**File:** `src/api/superclaude_api.py:197`
**Module:** `src.api.superclaude_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for enhance_prompt
- Consider adding UI control for enhance_prompt if user-facing
- Consider adding CLI command for enhance_prompt if appropriate

### initialize_synapse
**File:** `src/api/synapse_connector.py:214`
**Module:** `src.api.synapse_connector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for initialize_synapse
- Consider adding UI control for initialize_synapse if user-facing
- Consider adding CLI command for initialize_synapse if appropriate

### llm_health
**File:** `src/api/system_health.py:33`
**Module:** `src.api.system_health`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for llm_health
- Consider adding UI control for llm_health if user-facing
- Consider adding CLI command for llm_health if appropriate

### vault_health
**File:** `src/api/system_health.py:52`
**Module:** `src.api.system_health`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for vault_health
- Consider adding UI control for vault_health if user-facing
- Consider adding CLI command for vault_health if appropriate

### synapse_health
**File:** `src/api/system_health.py:70`
**Module:** `src.api.system_health`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for synapse_health
- Consider adding UI control for synapse_health if user-facing
- Consider adding CLI command for synapse_health if appropriate

### core_health
**File:** `src/api/system_health.py:89`
**Module:** `src.api.system_health`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for core_health
- Consider adding UI control for core_health if user-facing
- Consider adding CLI command for core_health if appropriate

### sentry_health
**File:** `src/api/system_health.py:106`
**Module:** `src.api.system_health`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for sentry_health
- Consider adding UI control for sentry_health if user-facing
- Consider adding CLI command for sentry_health if appropriate

### system_memory
**File:** `src/api/system_health.py:123`
**Module:** `src.api.system_health`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for system_memory
- Consider adding UI control for system_memory if user-facing
- Consider adding CLI command for system_memory if appropriate

### system_health
**File:** `src/api/system_health.py:144`
**Module:** `src.api.system_health`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for system_health
- Consider adding UI control for system_health if user-facing
- Consider adding CLI command for system_health if appropriate

### vault_stats
**File:** `src/api/system_health.py:203`
**Module:** `src.api.system_health`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for vault_stats
- Consider adding UI control for vault_stats if user-facing
- Consider adding CLI command for vault_stats if appropriate

### vault_memories
**File:** `src/api/system_health.py:223`
**Module:** `src.api.system_health`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for vault_memories
- Consider adding UI control for vault_memories if user-facing
- Consider adding CLI command for vault_memories if appropriate

### vault_audit_log
**File:** `src/api/system_health.py:265`
**Module:** `src.api.system_health`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for vault_audit_log
- Consider adding UI control for vault_audit_log if user-facing
- Consider adding CLI command for vault_audit_log if appropriate

### connect_llm
**File:** `src/api/system_health.py:304`
**Module:** `src.api.system_health`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for connect_llm
- Consider adding UI control for connect_llm if user-facing
- Consider adding CLI command for connect_llm if appropriate

### connect_vault
**File:** `src/api/system_health.py:318`
**Module:** `src.api.system_health`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for connect_vault
- Consider adding UI control for connect_vault if user-facing
- Consider adding CLI command for connect_vault if appropriate

### connect_synapse
**File:** `src/api/system_health.py:332`
**Module:** `src.api.system_health`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for connect_synapse
- Consider adding UI control for connect_synapse if user-facing
- Consider adding CLI command for connect_synapse if appropriate

### log_audit_entry
**File:** `src/api/task_templates.py:409`
**Module:** `src.api.task_templates`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_audit_entry
- Consider adding UI control for log_audit_entry if user-facing
- Consider adding CLI command for log_audit_entry if appropriate

### initialize_vault
**File:** `src/api/vault_api.py:31`
**Module:** `src.api.vault_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for initialize_vault
- Consider adding UI control for initialize_vault if user-facing
- Consider adding CLI command for initialize_vault if appropriate

### check_integrity
**File:** `src/api/vault_api.py:311`
**Module:** `src.api.vault_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_integrity
- Consider adding UI control for check_integrity if user-facing
- Consider adding CLI command for check_integrity if appropriate

### search_memories
**File:** `src/api/vault_api.py:331`
**Module:** `src.api.vault_api`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for search_memories
- Consider adding UI control for search_memories if user-facing
- Consider adding CLI command for search_memories if appropriate

### initialize_vault
**File:** `src/api/vault_connector.py:633`
**Module:** `src.api.vault_connector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for initialize_vault
- Consider adding UI control for initialize_vault if user-facing
- Consider adding CLI command for initialize_vault if appropriate

### encrypt_data
**File:** `src/api/vault_connector.py:103`
**Module:** `src.api.vault_connector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for encrypt_data
- Consider adding UI control for encrypt_data if user-facing
- Consider adding CLI command for encrypt_data if appropriate

### decrypt_data
**File:** `src/api/vault_connector.py:109`
**Module:** `src.api.vault_connector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for decrypt_data
- Consider adding UI control for decrypt_data if user-facing
- Consider adding CLI command for decrypt_data if appropriate

### store_persona
**File:** `src/api/vault_connector.py:118`
**Module:** `src.api.vault_connector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for store_persona
- Consider adding UI control for store_persona if user-facing
- Consider adding CLI command for store_persona if appropriate

### log_system_event
**File:** `src/api/vault_connector.py:226`
**Module:** `src.api.vault_connector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_system_event
- Consider adding UI control for log_system_event if user-facing
- Consider adding CLI command for log_system_event if appropriate

### check_integrity
**File:** `src/api/vault_connector.py:533`
**Module:** `src.api.vault_connector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_integrity
- Consider adding UI control for check_integrity if user-facing
- Consider adding CLI command for check_integrity if appropriate

### search_memories
**File:** `src/api/vault_connector.py:585`
**Module:** `src.api.vault_connector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for search_memories
- Consider adding UI control for search_memories if user-facing
- Consider adding CLI command for search_memories if appropriate

### load_config
**File:** `src/backend/alden_backend.py:43`
**Module:** `src.backend.alden_backend`
**Missing:** test, ui_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for load_config
- Consider adding UI control for load_config if user-facing

### startup_event
**File:** `src/backend/alden_backend.py:489`
**Module:** `src.backend.alden_backend`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for startup_event if user-facing
- Consider adding CLI command for startup_event if appropriate

### shutdown_event
**File:** `src/backend/alden_backend.py:494`
**Module:** `src.backend.alden_backend`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for shutdown_event if user-facing
- Consider adding CLI command for shutdown_event if appropriate

### process_query
**File:** `src/backend/alden_backend.py:512`
**Module:** `src.backend.alden_backend`
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for process_query if user-facing

### generate_embeddings
**File:** `src/backend/alden_backend.py:185`
**Module:** `src.backend.alden_backend`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_embeddings
- Consider adding UI control for generate_embeddings if user-facing
- Consider adding CLI command for generate_embeddings if appropriate

### rag_query
**File:** `src/backend/alden_backend.py:196`
**Module:** `src.backend.alden_backend`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for rag_query
- Consider adding UI control for rag_query if user-facing
- Consider adding CLI command for rag_query if appropriate

### retrieve_relevant_memories
**File:** `src/backend/alden_backend.py:219`
**Module:** `src.backend.alden_backend`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for retrieve_relevant_memories
- Consider adding UI control for retrieve_relevant_memories if user-facing
- Consider adding CLI command for retrieve_relevant_memories if appropriate

### build_context_text
**File:** `src/backend/alden_backend.py:256`
**Module:** `src.backend.alden_backend`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for build_context_text
- Consider adding UI control for build_context_text if user-facing
- Consider adding CLI command for build_context_text if appropriate

### generate_llm_response
**File:** `src/backend/alden_backend.py:274`
**Module:** `src.backend.alden_backend`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_llm_response
- Consider adding UI control for generate_llm_response if user-facing
- Consider adding CLI command for generate_llm_response if appropriate

### store_memory_slice
**File:** `src/backend/alden_backend.py:307`
**Module:** `src.backend.alden_backend`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for store_memory_slice
- Consider adding UI control for store_memory_slice if user-facing
- Consider adding CLI command for store_memory_slice if appropriate

### store_in_knowledge_graph
**File:** `src/backend/alden_backend.py:336`
**Module:** `src.backend.alden_backend`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for store_in_knowledge_graph
- Consider adding UI control for store_in_knowledge_graph if user-facing
- Consider adding CLI command for store_in_knowledge_graph if appropriate

### extract_entities
**File:** `src/backend/alden_backend.py:374`
**Module:** `src.backend.alden_backend`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for extract_entities
- Consider adding UI control for extract_entities if user-facing
- Consider adding CLI command for extract_entities if appropriate

### process_query
**File:** `src/backend/alden_backend.py:405`
**Module:** `src.backend.alden_backend`
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for process_query if user-facing

### generate_embedding
**File:** `src/embedding/semantic_embedding_service.py:128`
**Module:** `src.embedding.semantic_embedding_service`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for generate_embedding if user-facing
- Consider adding CLI command for generate_embedding if appropriate

### generate_embeddings_batch
**File:** `src/embedding/semantic_embedding_service.py:198`
**Module:** `src.embedding.semantic_embedding_service`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_embeddings_batch
- Consider adding UI control for generate_embeddings_batch if user-facing
- Consider adding CLI command for generate_embeddings_batch if appropriate

### embed_memory_slice
**File:** `src/embedding/semantic_embedding_service.py:298`
**Module:** `src.embedding.semantic_embedding_service`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for embed_memory_slice
- Consider adding UI control for embed_memory_slice if user-facing
- Consider adding CLI command for embed_memory_slice if appropriate

### clear_cache
**File:** `src/embedding/semantic_embedding_service.py:363`
**Module:** `src.embedding.semantic_embedding_service`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for clear_cache
- Consider adding UI control for clear_cache if user-facing
- Consider adding CLI command for clear_cache if appropriate

### store_memory_with_embedding
**File:** `src/embedding/semantic_embedding_service.py:411`
**Module:** `src.embedding.semantic_embedding_service`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for store_memory_with_embedding
- Consider adding UI control for store_memory_with_embedding if user-facing
- Consider adding CLI command for store_memory_with_embedding if appropriate

### semantic_retrieve
**File:** `src/embedding/semantic_embedding_service.py:465`
**Module:** `src.embedding.semantic_embedding_service`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for semantic_retrieve
- Consider adding UI control for semantic_retrieve if user-facing
- Consider adding CLI command for semantic_retrieve if appropriate

### hybrid_retrieve
**File:** `src/embedding/semantic_embedding_service.py:513`
**Module:** `src.embedding.semantic_embedding_service`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for hybrid_retrieve
- Consider adding UI control for hybrid_retrieve if user-facing
- Consider adding CLI command for hybrid_retrieve if appropriate

### select_optimal_model
**File:** `src/llm/llm_selection_layer.py:397`
**Module:** `src.llm.llm_selection_layer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for select_optimal_model
- Consider adding UI control for select_optimal_model if user-facing
- Consider adding CLI command for select_optimal_model if appropriate

### switch_model
**File:** `src/llm/llm_selection_layer.py:501`
**Module:** `src.llm.llm_selection_layer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for switch_model
- Consider adding UI control for switch_model if user-facing
- Consider adding CLI command for switch_model if appropriate

### generate_with_current_model
**File:** `src/llm/llm_selection_layer.py:625`
**Module:** `src.llm.llm_selection_layer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_with_current_model
- Consider adding UI control for generate_with_current_model if user-facing
- Consider adding CLI command for generate_with_current_model if appropriate

### shutdown
**File:** `src/llm/llm_selection_layer.py:701`
**Module:** `src.llm.llm_selection_layer`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for shutdown if user-facing
- Consider adding CLI command for shutdown if appropriate

### health_check_worker
**File:** `src/llm/llm_selection_layer.py:360`
**Module:** `src.llm.llm_selection_layer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for health_check_worker
- Consider adding UI control for health_check_worker if user-facing
- Consider adding CLI command for health_check_worker if appropriate

### record_error
**File:** `src/llm/local_llm_client.py:213`
**Module:** `src.llm.local_llm_client`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for record_error
- Consider adding UI control for record_error if user-facing
- Consider adding CLI command for record_error if appropriate

### record_success
**File:** `src/llm/local_llm_client.py:220`
**Module:** `src.llm.local_llm_client`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for record_success
- Consider adding UI control for record_success if user-facing
- Consider adding CLI command for record_success if appropriate

### list_models
**File:** `src/llm/local_llm_client.py:683`
**Module:** `src.llm.local_llm_client`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for list_models
- Consider adding UI control for list_models if user-facing
- Consider adding CLI command for list_models if appropriate

### log_agent_token_usage
**File:** `src/log_handling/agent_token_tracker.py:474`
**Module:** `src.log_handling.agent_token_tracker`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_agent_token_usage
- Consider adding UI control for log_agent_token_usage if user-facing
- Consider adding CLI command for log_agent_token_usage if appropriate

### log_token_usage
**File:** `src/log_handling/agent_token_tracker.py:160`
**Module:** `src.log_handling.agent_token_tracker`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_token_usage
- Consider adding UI control for log_token_usage if user-facing
- Consider adding CLI command for log_token_usage if appropriate

### export_logs
**File:** `src/log_handling/agent_token_tracker.py:358`
**Module:** `src.log_handling.agent_token_tracker`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_logs
- Consider adding UI control for export_logs if user-facing
- Consider adding CLI command for export_logs if appropriate

### log_exception
**File:** `src/log_handling/exception_handler.py:496`
**Module:** `src.log_handling.exception_handler`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_exception
- Consider adding UI control for log_exception if user-facing
- Consider adding CLI command for log_exception if appropriate

### log_error
**File:** `src/log_handling/exception_handler.py:519`
**Module:** `src.log_handling.exception_handler`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for log_error if user-facing
- Consider adding CLI command for log_error if appropriate

### log_exception
**File:** `src/log_handling/exception_handler.py:236`
**Module:** `src.log_handling.exception_handler`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for log_exception
- Consider adding UI control for log_exception if user-facing
- Consider adding CLI command for log_exception if appropriate

### log_error
**File:** `src/log_handling/exception_handler.py:312`
**Module:** `src.log_handling.exception_handler`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for log_error if user-facing
- Consider adding CLI command for log_error if appropriate

### set_log_level
**File:** `src/log_handling/exception_handler.py:381`
**Module:** `src.log_handling.exception_handler`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for set_log_level
- Consider adding UI control for set_log_level if user-facing
- Consider adding CLI command for set_log_level if appropriate

### export_logs
**File:** `src/log_handling/exception_handler.py:387`
**Module:** `src.log_handling.exception_handler`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_logs
- Consider adding UI control for export_logs if user-facing
- Consider adding CLI command for export_logs if appropriate

### clear_logs
**File:** `src/log_handling/exception_handler.py:472`
**Module:** `src.log_handling.exception_handler`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for clear_logs
- Consider adding UI control for clear_logs if user-facing
- Consider adding CLI command for clear_logs if appropriate

### analyze_conversations
**File:** `src/memory/memory_pruning_manager.py:130`
**Module:** `src.memory.memory_pruning_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for analyze_conversations
- Consider adding UI control for analyze_conversations if user-facing
- Consider adding CLI command for analyze_conversations if appropriate

### prune_conversations
**File:** `src/memory/memory_pruning_manager.py:301`
**Module:** `src.memory.memory_pruning_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for prune_conversations
- Consider adding UI control for prune_conversations if user-facing
- Consider adding CLI command for prune_conversations if appropriate

### generate_persona
**File:** `src/personas/mimic.py:371`
**Module:** `src.personas.mimic`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for generate_persona if user-facing
- Consider adding CLI command for generate_persona if appropriate

### record_performance
**File:** `src/personas/mimic.py:634`
**Module:** `src.personas.mimic`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for record_performance if user-facing
- Consider adding CLI command for record_performance if appropriate

### fork_persona
**File:** `src/personas/mimic.py:776`
**Module:** `src.personas.mimic`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for fork_persona if user-facing
- Consider adding CLI command for fork_persona if appropriate

### merge_personas
**File:** `src/personas/mimic.py:830`
**Module:** `src.personas.mimic`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for merge_personas if user-facing
- Consider adding CLI command for merge_personas if appropriate

### add_plugin_extension
**File:** `src/personas/mimic.py:927`
**Module:** `src.personas.mimic`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for add_plugin_extension if user-facing
- Consider adding CLI command for add_plugin_extension if appropriate

### export_memory
**File:** `src/personas/mimic.py:1115`
**Module:** `src.personas.mimic`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for export_memory
- Consider adding UI control for export_memory if user-facing
- Consider adding CLI command for export_memory if appropriate

### import_memory
**File:** `src/personas/mimic.py:1140`
**Module:** `src.personas.mimic`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for import_memory
- Consider adding UI control for import_memory if user-facing
- Consider adding CLI command for import_memory if appropriate

### acquire_memory_lock
**File:** `src/services/memory_sync_service.py:244`
**Module:** `src.services.memory_sync_service`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for acquire_memory_lock
- Consider adding UI control for acquire_memory_lock if user-facing
- Consider adding CLI command for acquire_memory_lock if appropriate

### release_memory_lock
**File:** `src/services/memory_sync_service.py:321`
**Module:** `src.services.memory_sync_service`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for release_memory_lock
- Consider adding UI control for release_memory_lock if user-facing
- Consider adding CLI command for release_memory_lock if appropriate

### sync_agent_memories
**File:** `src/services/memory_sync_service.py:365`
**Module:** `src.services.memory_sync_service`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for sync_agent_memories
- Consider adding UI control for sync_agent_memories if user-facing
- Consider adding CLI command for sync_agent_memories if appropriate

### resolve_conflict
**File:** `src/services/memory_sync_service.py:482`
**Module:** `src.services.memory_sync_service`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for resolve_conflict
- Consider adding UI control for resolve_conflict if user-facing
- Consider adding CLI command for resolve_conflict if appropriate

### sync_worker
**File:** `src/services/memory_sync_service.py:192`
**Module:** `src.services.memory_sync_service`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for sync_worker
- Consider adding UI control for sync_worker if user-facing
- Consider adding CLI command for sync_worker if appropriate

### semantic_search
**File:** `src/services/memory_sync_service.py:1115`
**Module:** `src.services.memory_sync_service`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for semantic_search if user-facing
- Consider adding CLI command for semantic_search if appropriate

### register_agent
**File:** `src/services/multi_agent_memory_coordinator.py:236`
**Module:** `src.services.multi_agent_memory_coordinator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for register_agent
- Consider adding UI control for register_agent if user-facing
- Consider adding CLI command for register_agent if appropriate

### store_agent_memory
**File:** `src/services/multi_agent_memory_coordinator.py:285`
**Module:** `src.services.multi_agent_memory_coordinator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for store_agent_memory
- Consider adding UI control for store_agent_memory if user-facing
- Consider adding CLI command for store_agent_memory if appropriate

### search_agent_memories
**File:** `src/services/multi_agent_memory_coordinator.py:402`
**Module:** `src.services.multi_agent_memory_coordinator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for search_agent_memories
- Consider adding UI control for search_agent_memories if user-facing
- Consider adding CLI command for search_agent_memories if appropriate

### sync_all_agents
**File:** `src/services/multi_agent_memory_coordinator.py:494`
**Module:** `src.services.multi_agent_memory_coordinator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for sync_all_agents
- Consider adding UI control for sync_all_agents if user-facing
- Consider adding CLI command for sync_all_agents if appropriate

### start_automatic_recovery
**File:** `src/utils/automatic_recovery_orchestrator.py:664`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_automatic_recovery
- Consider adding UI control for start_automatic_recovery if user-facing
- Consider adding CLI command for start_automatic_recovery if appropriate

### stop_automatic_recovery
**File:** `src/utils/automatic_recovery_orchestrator.py:668`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for stop_automatic_recovery
- Consider adding UI control for stop_automatic_recovery if user-facing
- Consider adding CLI command for stop_automatic_recovery if appropriate

### force_service_recovery
**File:** `src/utils/automatic_recovery_orchestrator.py:676`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for force_service_recovery
- Consider adding UI control for force_service_recovery if user-facing
- Consider adding CLI command for force_service_recovery if appropriate

### register_event_callback
**File:** `src/utils/automatic_recovery_orchestrator.py:176`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for register_event_callback
- Consider adding UI control for register_event_callback if user-facing
- Consider adding CLI command for register_event_callback if appropriate

### assess_system_health
**File:** `src/utils/automatic_recovery_orchestrator.py:189`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for assess_system_health
- Consider adding UI control for assess_system_health if user-facing
- Consider adding CLI command for assess_system_health if appropriate

### detect_service_failures
**File:** `src/utils/automatic_recovery_orchestrator.py:241`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for detect_service_failures
- Consider adding UI control for detect_service_failures if user-facing
- Consider adding CLI command for detect_service_failures if appropriate

### queue_recovery
**File:** `src/utils/automatic_recovery_orchestrator.py:266`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for queue_recovery
- Consider adding UI control for queue_recovery if user-facing
- Consider adding CLI command for queue_recovery if appropriate

### recovery_worker
**File:** `src/utils/automatic_recovery_orchestrator.py:396`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for recovery_worker
- Consider adding UI control for recovery_worker if user-facing
- Consider adding CLI command for recovery_worker if appropriate

### monitoring_loop
**File:** `src/utils/automatic_recovery_orchestrator.py:520`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for monitoring_loop
- Consider adding UI control for monitoring_loop if user-facing
- Consider adding CLI command for monitoring_loop if appropriate

### start_orchestrator
**File:** `src/utils/automatic_recovery_orchestrator.py:551`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_orchestrator
- Consider adding UI control for start_orchestrator if user-facing
- Consider adding CLI command for start_orchestrator if appropriate

### stop_orchestrator
**File:** `src/utils/automatic_recovery_orchestrator.py:579`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for stop_orchestrator
- Consider adding UI control for stop_orchestrator if user-facing
- Consider adding CLI command for stop_orchestrator if appropriate

### generate_status_report
**File:** `src/utils/automatic_recovery_orchestrator.py:618`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_status_report
- Consider adding UI control for generate_status_report if user-facing
- Consider adding CLI command for generate_status_report if appropriate

### signal_handler
**File:** `src/utils/automatic_recovery_orchestrator.py:699`
**Module:** `src.utils.automatic_recovery_orchestrator`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for signal_handler
- Consider adding UI control for signal_handler if user-facing
- Consider adding CLI command for signal_handler if appropriate

### with_circuit_breaker
**File:** `src/utils/circuit_breaker.py:307`
**Module:** `src.utils.circuit_breaker`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for with_circuit_breaker
- Consider adding UI control for with_circuit_breaker if user-facing
- Consider adding CLI command for with_circuit_breaker if appropriate

### record_success
**File:** `src/utils/circuit_breaker.py:46`
**Module:** `src.utils.circuit_breaker`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for record_success
- Consider adding UI control for record_success if user-facing
- Consider adding CLI command for record_success if appropriate

### record_failure
**File:** `src/utils/circuit_breaker.py:52`
**Module:** `src.utils.circuit_breaker`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for record_failure
- Consider adding UI control for record_failure if user-facing
- Consider adding CLI command for record_failure if appropriate

### record_state_change
**File:** `src/utils/circuit_breaker.py:59`
**Module:** `src.utils.circuit_breaker`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for record_state_change
- Consider adding UI control for record_state_change if user-facing
- Consider adding CLI command for record_state_change if appropriate

### to_dict
**File:** `src/utils/circuit_breaker.py:83`
**Module:** `src.utils.circuit_breaker`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for to_dict
- Consider adding UI control for to_dict if user-facing
- Consider adding CLI command for to_dict if appropriate

### reset
**File:** `src/utils/circuit_breaker.py:242`
**Module:** `src.utils.circuit_breaker`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for reset if user-facing
- Consider adding CLI command for reset if appropriate

### reset_all
**File:** `src/utils/circuit_breaker.py:290`
**Module:** `src.utils.circuit_breaker`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for reset_all if user-facing
- Consider adding CLI command for reset_all if appropriate

### remove_breaker
**File:** `src/utils/circuit_breaker.py:297`
**Module:** `src.utils.circuit_breaker`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for remove_breaker
- Consider adding UI control for remove_breaker if user-facing
- Consider adding CLI command for remove_breaker if appropriate

### decorator
**File:** `src/utils/circuit_breaker.py:320`
**Module:** `src.utils.circuit_breaker`
**Missing:** test, ui_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for decorator
- Consider adding UI control for decorator if user-facing

### unreliable_service
**File:** `src/utils/circuit_breaker.py:331`
**Module:** `src.utils.circuit_breaker`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for unreliable_service
- Consider adding UI control for unreliable_service if user-facing
- Consider adding CLI command for unreliable_service if appropriate

### wrapper
**File:** `src/utils/circuit_breaker.py:321`
**Module:** `src.utils.circuit_breaker`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for wrapper
- Consider adding UI control for wrapper if user-facing
- Consider adding CLI command for wrapper if appropriate

### validate_environment
**File:** `src/utils/env_loader.py:300`
**Module:** `src.utils.env_loader`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_environment
- Consider adding UI control for validate_environment if user-facing
- Consider adding CLI command for validate_environment if appropriate

### load_environment
**File:** `src/utils/env_loader.py:77`
**Module:** `src.utils.env_loader`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for load_environment
- Consider adding UI control for load_environment if user-facing
- Consider adding CLI command for load_environment if appropriate

### validate_required_vars
**File:** `src/utils/env_loader.py:170`
**Module:** `src.utils.env_loader`
**Missing:** test, ui_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for validate_required_vars
- Consider adding UI control for validate_required_vars if user-facing

### optimize_memory_storage
**File:** `src/utils/memory_optimizer.py:30`
**Module:** `src.utils.memory_optimizer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for optimize_memory_storage
- Consider adding UI control for optimize_memory_storage if user-facing
- Consider adding CLI command for optimize_memory_storage if appropriate

### consolidate_alden_memory
**File:** `src/utils/memory_optimizer.py:66`
**Module:** `src.utils.memory_optimizer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for consolidate_alden_memory
- Consider adding UI control for consolidate_alden_memory if user-facing
- Consider adding CLI command for consolidate_alden_memory if appropriate

### merge_memory_file
**File:** `src/utils/memory_optimizer.py:160`
**Module:** `src.utils.memory_optimizer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for merge_memory_file
- Consider adding UI control for merge_memory_file if user-facing
- Consider adding CLI command for merge_memory_file if appropriate

### insert_consolidated_record
**File:** `src/utils/memory_optimizer.py:196`
**Module:** `src.utils.memory_optimizer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for insert_consolidated_record
- Consider adding UI control for insert_consolidated_record if user-facing
- Consider adding CLI command for insert_consolidated_record if appropriate

### optimize_vault_storage
**File:** `src/utils/memory_optimizer.py:281`
**Module:** `src.utils.memory_optimizer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for optimize_vault_storage
- Consider adding UI control for optimize_vault_storage if user-facing
- Consider adding CLI command for optimize_vault_storage if appropriate

### archive_old_sessions
**File:** `src/utils/memory_optimizer.py:305`
**Module:** `src.utils.memory_optimizer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for archive_old_sessions
- Consider adding UI control for archive_old_sessions if user-facing
- Consider adding CLI command for archive_old_sessions if appropriate

### generate_cache_key
**File:** `src/utils/performance_optimizer.py:59`
**Module:** `src.utils.performance_optimizer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_cache_key
- Consider adding UI control for generate_cache_key if user-facing
- Consider adding CLI command for generate_cache_key if appropriate

### cache_response
**File:** `src/utils/performance_optimizer.py:109`
**Module:** `src.utils.performance_optimizer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for cache_response
- Consider adding UI control for cache_response if user-facing
- Consider adding CLI command for cache_response if appropriate

### optimize_prompt
**File:** `src/utils/performance_optimizer.py:192`
**Module:** `src.utils.performance_optimizer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for optimize_prompt
- Consider adding UI control for optimize_prompt if user-facing
- Consider adding CLI command for optimize_prompt if appropriate

### optimize_llm_request
**File:** `src/utils/performance_optimizer.py:258`
**Module:** `src.utils.performance_optimizer`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for optimize_llm_request
- Consider adding UI control for optimize_llm_request if user-facing
- Consider adding CLI command for optimize_llm_request if appropriate

### make_request
**File:** `src/utils/performance_optimizer.py:344`
**Module:** `src.utils.performance_optimizer`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for make_request if user-facing
- Consider adding CLI command for make_request if appropriate

### start_service_recovery
**File:** `src/utils/service_recovery_manager.py:666`
**Module:** `src.utils.service_recovery_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_service_recovery
- Consider adding UI control for start_service_recovery if user-facing
- Consider adding CLI command for start_service_recovery if appropriate

### stop_service_recovery
**File:** `src/utils/service_recovery_manager.py:670`
**Module:** `src.utils.service_recovery_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for stop_service_recovery
- Consider adding UI control for stop_service_recovery if user-facing
- Consider adding CLI command for stop_service_recovery if appropriate

### check_service_health
**File:** `src/utils/service_recovery_manager.py:171`
**Module:** `src.utils.service_recovery_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_service_health
- Consider adding UI control for check_service_health if user-facing
- Consider adding CLI command for check_service_health if appropriate

### restart_service
**File:** `src/utils/service_recovery_manager.py:277`
**Module:** `src.utils.service_recovery_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for restart_service
- Consider adding UI control for restart_service if user-facing
- Consider adding CLI command for restart_service if appropriate

### heal_service
**File:** `src/utils/service_recovery_manager.py:383`
**Module:** `src.utils.service_recovery_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for heal_service
- Consider adding UI control for heal_service if user-facing
- Consider adding CLI command for heal_service if appropriate

### failover_service
**File:** `src/utils/service_recovery_manager.py:438`
**Module:** `src.utils.service_recovery_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for failover_service
- Consider adding UI control for failover_service if user-facing
- Consider adding CLI command for failover_service if appropriate

### emergency_stop_service
**File:** `src/utils/service_recovery_manager.py:461`
**Module:** `src.utils.service_recovery_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for emergency_stop_service
- Consider adding UI control for emergency_stop_service if user-facing
- Consider adding CLI command for emergency_stop_service if appropriate

### monitor_services
**File:** `src/utils/service_recovery_manager.py:489`
**Module:** `src.utils.service_recovery_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for monitor_services
- Consider adding UI control for monitor_services if user-facing
- Consider adding CLI command for monitor_services if appropriate

### start_monitoring
**File:** `src/utils/service_recovery_manager.py:591`
**Module:** `src.utils.service_recovery_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_monitoring
- Consider adding UI control for start_monitoring if user-facing
- Consider adding CLI command for start_monitoring if appropriate

### stop_monitoring
**File:** `src/utils/service_recovery_manager.py:604`
**Module:** `src.utils.service_recovery_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for stop_monitoring
- Consider adding UI control for stop_monitoring if user-facing
- Consider adding CLI command for stop_monitoring if appropriate

### generate_recovery_report
**File:** `src/utils/service_recovery_manager.py:626`
**Module:** `src.utils.service_recovery_manager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for generate_recovery_report
- Consider adding UI control for generate_recovery_report if user-facing
- Consider adding CLI command for generate_recovery_report if appropriate

### is_port_in_use
**File:** `src/utils/service_watchdog.py:80`
**Module:** `src.utils.service_watchdog`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for is_port_in_use
- Consider adding UI control for is_port_in_use if user-facing
- Consider adding CLI command for is_port_in_use if appropriate

### start_service
**File:** `src/utils/service_watchdog.py:87`
**Module:** `src.utils.service_watchdog`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_service
- Consider adding UI control for start_service if user-facing
- Consider adding CLI command for start_service if appropriate

### stop_service
**File:** `src/utils/service_watchdog.py:133`
**Module:** `src.utils.service_watchdog`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for stop_service
- Consider adding UI control for stop_service if user-facing
- Consider adding CLI command for stop_service if appropriate

### restart_service
**File:** `src/utils/service_watchdog.py:162`
**Module:** `src.utils.service_watchdog`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for restart_service
- Consider adding UI control for restart_service if user-facing
- Consider adding CLI command for restart_service if appropriate

### check_service_health
**File:** `src/utils/service_watchdog.py:176`
**Module:** `src.utils.service_watchdog`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for check_service_health
- Consider adding UI control for check_service_health if user-facing
- Consider adding CLI command for check_service_health if appropriate

### monitor_services
**File:** `src/utils/service_watchdog.py:194`
**Module:** `src.utils.service_watchdog`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for monitor_services
- Consider adding UI control for monitor_services if user-facing
- Consider adding CLI command for monitor_services if appropriate

### start_all_services
**File:** `src/utils/service_watchdog.py:236`
**Module:** `src.utils.service_watchdog`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for start_all_services
- Consider adding UI control for start_all_services if user-facing
- Consider adding CLI command for start_all_services if appropriate

### stop_all_services
**File:** `src/utils/service_watchdog.py:248`
**Module:** `src.utils.service_watchdog`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for stop_all_services
- Consider adding UI control for stop_all_services if user-facing
- Consider adding CLI command for stop_all_services if appropriate

### signal_handler
**File:** `src/utils/service_watchdog.py:327`
**Module:** `src.utils.service_watchdog`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add pytest unit test in tests/unit/ for signal_handler
- Consider adding UI control for signal_handler if user-facing
- Consider adding CLI command for signal_handler if appropriate

### run_comprehensive_validation
**File:** `scripts/alpha_readiness_test.py:414`
**Module:** `scripts.alpha_readiness_test`
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for run_comprehensive_validation if user-facing

### scan_repository
**File:** `scripts/function_inventory.py:113`
**Module:** `scripts.function_inventory`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for scan_repository
- Consider adding UI control for scan_repository if user-facing

### validate_spec2_components
**File:** `scripts/run_performance_tests.py:163`
**Module:** `scripts.run_performance_tests`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for validate_spec2_components
- Consider adding UI control for validate_spec2_components if user-facing

### calculate_overall_performance_grade
**File:** `scripts/run_performance_tests.py:248`
**Module:** `scripts.run_performance_tests`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for calculate_overall_performance_grade
- Consider adding UI control for calculate_overall_performance_grade if user-facing

### generate_comprehensive_report
**File:** `scripts/run_performance_tests.py:273`
**Module:** `scripts.run_performance_tests`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for generate_comprehensive_report
- Consider adding UI control for generate_comprehensive_report if user-facing

### load_config
**File:** `scripts/setup_databases.py:22`
**Module:** `scripts.setup_databases`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for load_config
- Consider adding UI control for load_config if user-facing

### calculate_file_hash
**File:** `scripts/validate_installer.py:15`
**Module:** `scripts.validate_installer`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for calculate_file_hash
- Consider adding UI control for calculate_file_hash if user-facing

### validate_spec2_components
**File:** `scripts/validate_installer.py:27`
**Module:** `scripts.validate_installer`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for validate_spec2_components
- Consider adding UI control for validate_spec2_components if user-facing

### validate_assets
**File:** `scripts/validate_installer.py:59`
**Module:** `scripts.validate_installer`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for validate_assets
- Consider adding UI control for validate_assets if user-facing

### validate_tauri_config
**File:** `scripts/validate_installer.py:98`
**Module:** `scripts.validate_installer`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for validate_tauri_config
- Consider adding UI control for validate_tauri_config if user-facing

### validate_package_json
**File:** `scripts/validate_installer.py:134`
**Module:** `scripts.validate_installer`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for validate_package_json
- Consider adding UI control for validate_package_json if user-facing

### check_build_artifacts
**File:** `scripts/validate_installer.py:159`
**Module:** `scripts.validate_installer`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for check_build_artifacts
- Consider adding UI control for check_build_artifacts if user-facing

### generate_validation_report
**File:** `scripts/validate_installer.py:183`
**Module:** `scripts.validate_installer`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for generate_validation_report
- Consider adding UI control for generate_validation_report if user-facing

### show_status
**File:** `scripts/vault_rotation_cli.py:420`
**Module:** `scripts.vault_rotation_cli`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for show_status
- Consider adding UI control for show_status if user-facing

### check_file_existence
**File:** `scripts/verify_env.py:66`
**Module:** `scripts.verify_env`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for check_file_existence
- Consider adding UI control for check_file_existence if user-facing

### parse_env_file
**File:** `scripts/verify_env.py:88`
**Module:** `scripts.verify_env`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for parse_env_file
- Consider adding UI control for parse_env_file if user-facing

### validate_variable_formats
**File:** `scripts/verify_env.py:125`
**Module:** `scripts.verify_env`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for validate_variable_formats
- Consider adding UI control for validate_variable_formats if user-facing

### check_variable_completeness
**File:** `scripts/verify_env.py:158`
**Module:** `scripts.verify_env`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for check_variable_completeness
- Consider adding UI control for check_variable_completeness if user-facing

### validate_with_loader
**File:** `scripts/verify_env.py:182`
**Module:** `scripts.verify_env`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for validate_with_loader
- Consider adding UI control for validate_with_loader if user-facing

### check_security_issues
**File:** `scripts/verify_env.py:217`
**Module:** `scripts.verify_env`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for check_security_issues
- Consider adding UI control for check_security_issues if user-facing

### load_config_schema
**File:** `scripts/verify_env.py:239`
**Module:** `scripts.verify_env`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for load_config_schema
- Consider adding UI control for load_config_schema if user-facing

### validate_config_files
**File:** `scripts/verify_env.py:253`
**Module:** `scripts.verify_env`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for validate_config_files
- Consider adding UI control for validate_config_files if user-facing

### validate_cross_service_config_alignment
**File:** `scripts/verify_env.py:311`
**Module:** `scripts.verify_env`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for validate_cross_service_config_alignment
- Consider adding UI control for validate_cross_service_config_alignment if user-facing

### validate_required_env_vars_strict
**File:** `scripts/verify_env.py:382`
**Module:** `scripts.verify_env`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for validate_required_env_vars_strict
- Consider adding UI control for validate_required_env_vars_strict if user-facing

### print_results
**File:** `scripts/verify_env.py:516`
**Module:** `scripts.verify_env`
**Missing:** test, ui_invocation

**Recommendations:**
- Add appropriate unit test for print_results
- Consider adding UI control for print_results if user-facing

### EmbeddedGrafana
**File:** `src/components/EmbeddedGrafana.tsx:101`
**Module:** `src.components.EmbeddedGrafana`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add React Testing Library test in tests/components/ for EmbeddedGrafana
- Ensure EmbeddedGrafana component is imported and used in parent components
- Consider adding CLI command for EmbeddedGrafana if appropriate

### LaunchPage
**File:** `src/components/LaunchPage.tsx:22`
**Module:** `src.components.LaunchPage`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add React Testing Library test in tests/components/ for LaunchPage
- Ensure LaunchPage component is imported and used in parent components
- Consider adding CLI command for LaunchPage if appropriate

### Button
**File:** `src/components/ui/index.tsx:74`
**Module:** `src.components.ui.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Ensure Button component is imported and used in parent components
- Consider adding CLI command for Button if appropriate

### Input
**File:** `src/components/ui/index.tsx:110`
**Module:** `src.components.ui.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Ensure Input component is imported and used in parent components
- Consider adding CLI command for Input if appropriate

### Alert
**File:** `src/components/ui/index.tsx:151`
**Module:** `src.components.ui.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Ensure Alert component is imported and used in parent components
- Consider adding CLI command for Alert if appropriate

### useClaudeConnector
**File:** `src/hooks/useClaudeConnector.ts:70`
**Module:** `src.hooks.useClaudeConnector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useClaudeConnector
- Consider adding UI control for useClaudeConnector if user-facing
- Consider adding CLI command for useClaudeConnector if appropriate

### useClaudeChat
**File:** `src/hooks/useClaudeConnector.ts:174`
**Module:** `src.hooks.useClaudeConnector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useClaudeChat
- Consider adding UI control for useClaudeChat if user-facing
- Consider adding CLI command for useClaudeChat if appropriate

### useClaudeChat
**File:** `src/hooks/useClaudeConnector.ts:174`
**Module:** `src.hooks.useClaudeConnector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useClaudeChat
- Consider adding UI control for useClaudeChat if user-facing
- Consider adding CLI command for useClaudeChat if appropriate

### useClaudeCodeGen
**File:** `src/hooks/useClaudeConnector.ts:196`
**Module:** `src.hooks.useClaudeConnector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useClaudeCodeGen
- Consider adding UI control for useClaudeCodeGen if user-facing
- Consider adding CLI command for useClaudeCodeGen if appropriate

### useClaudeCodeGen
**File:** `src/hooks/useClaudeConnector.ts:196`
**Module:** `src.hooks.useClaudeConnector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useClaudeCodeGen
- Consider adding UI control for useClaudeCodeGen if user-facing
- Consider adding CLI command for useClaudeCodeGen if appropriate

### useClaudeAnalysis
**File:** `src/hooks/useClaudeConnector.ts:225`
**Module:** `src.hooks.useClaudeConnector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useClaudeAnalysis
- Consider adding UI control for useClaudeAnalysis if user-facing
- Consider adding CLI command for useClaudeAnalysis if appropriate

### useClaudeAnalysis
**File:** `src/hooks/useClaudeConnector.ts:225`
**Module:** `src.hooks.useClaudeConnector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useClaudeAnalysis
- Consider adding UI control for useClaudeAnalysis if user-facing
- Consider adding CLI command for useClaudeAnalysis if appropriate

### useClaudeDocumentProcessor
**File:** `src/hooks/useClaudeConnector.ts:254`
**Module:** `src.hooks.useClaudeConnector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useClaudeDocumentProcessor
- Consider adding UI control for useClaudeDocumentProcessor if user-facing
- Add CLI command wrapper for useClaudeDocumentProcessor

### useClaudeDocumentProcessor
**File:** `src/hooks/useClaudeConnector.ts:254`
**Module:** `src.hooks.useClaudeConnector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useClaudeDocumentProcessor
- Consider adding UI control for useClaudeDocumentProcessor if user-facing
- Add CLI command wrapper for useClaudeDocumentProcessor

### useKimiK2Chat
**File:** `src/hooks/useKimiK2.ts:154`
**Module:** `src.hooks.useKimiK2`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useKimiK2Chat
- Consider adding UI control for useKimiK2Chat if user-facing
- Consider adding CLI command for useKimiK2Chat if appropriate

### useKimiK2CodeGen
**File:** `src/hooks/useKimiK2.ts:182`
**Module:** `src.hooks.useKimiK2`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useKimiK2CodeGen
- Consider adding UI control for useKimiK2CodeGen if user-facing
- Consider adding CLI command for useKimiK2CodeGen if appropriate

### useKimiK2Agentic
**File:** `src/hooks/useKimiK2.ts:212`
**Module:** `src.hooks.useKimiK2`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useKimiK2Agentic
- Consider adding UI control for useKimiK2Agentic if user-facing
- Consider adding CLI command for useKimiK2Agentic if appropriate

### useKimiK2LongContext
**File:** `src/hooks/useKimiK2.ts:244`
**Module:** `src.hooks.useKimiK2`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useKimiK2LongContext
- Consider adding UI control for useKimiK2LongContext if user-facing
- Consider adding CLI command for useKimiK2LongContext if appropriate

### useKimiK2Analysis
**File:** `src/hooks/useKimiK2.ts:276`
**Module:** `src.hooks.useKimiK2`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useKimiK2Analysis
- Consider adding UI control for useKimiK2Analysis if user-facing
- Consider adding CLI command for useKimiK2Analysis if appropriate

### useTauriIntegration
**File:** `src/hooks/useTauriIntegration.ts:49`
**Module:** `src.hooks.useTauriIntegration`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useTauriIntegration
- Consider adding UI control for useTauriIntegration if user-facing
- Consider adding CLI command for useTauriIntegration if appropriate

### isTauriApp
**File:** `src/hooks/useTauriIntegration.ts:292`
**Module:** `src.hooks.useTauriIntegration`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for isTauriApp
- Consider adding UI control for isTauriApp if user-facing
- Consider adding CLI command for isTauriApp if appropriate

### useTauriFileSystem
**File:** `src/hooks/useTauriIntegration.ts:297`
**Module:** `src.hooks.useTauriIntegration`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useTauriFileSystem
- Consider adding UI control for useTauriFileSystem if user-facing
- Consider adding CLI command for useTauriFileSystem if appropriate

### useTauriFileSystem
**File:** `src/hooks/useTauriIntegration.ts:297`
**Module:** `src.hooks.useTauriIntegration`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for useTauriFileSystem
- Consider adding UI control for useTauriFileSystem if user-facing
- Consider adding CLI command for useTauriFileSystem if appropriate

### createClaudeConnector
**File:** `src/llm/ClaudeConnector.ts:458`
**Module:** `src.llm.ClaudeConnector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for createClaudeConnector
- Consider adding UI control for createClaudeConnector if user-facing
- Consider adding CLI command for createClaudeConnector if appropriate

### getClaudeConnector
**File:** `src/llm/ClaudeConnector.ts:466`
**Module:** `src.llm.ClaudeConnector`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getClaudeConnector
- Consider adding UI control for getClaudeConnector if user-facing
- Consider adding CLI command for getClaudeConnector if appropriate

### constructor
**File:** `src/personas/sentry/sentry.ts:86`
**Module:** `src.personas.sentry.sentry`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for constructor if user-facing
- Consider adding CLI command for constructor if appropriate

### catch
**File:** `src/personas/sentry/sentry.ts:156`
**Module:** `src.personas.sentry.sentry`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `src/personas/sentry/sentry.ts:194`
**Module:** `src.personas.sentry.sentry`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `src/personas/sentry/sentry.ts:225`
**Module:** `src.personas.sentry.sentry`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `src/personas/sentry/sentry.ts:264`
**Module:** `src.personas.sentry.sentry`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `src/personas/sentry/sentry.ts:295`
**Module:** `src.personas.sentry.sentry`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `src/personas/sentry/sentry.ts:331`
**Module:** `src.personas.sentry.sentry`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `src/personas/sentry/sentry.ts:350`
**Module:** `src.personas.sentry.sentry`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### getModuleComponent
**File:** `src/App.js:542`
**Module:** `src.App`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add React Testing Library test in tests/components/ for getModuleComponent
- Ensure getModuleComponent component is imported and used in parent components
- Consider adding CLI command for getModuleComponent if appropriate

### exportApiConfiguration
**File:** `src/components/SynapseGateway.js:674`
**Module:** `src.components.SynapseGateway`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for exportApiConfiguration
- Add UI button/form calling exportApiConfiguration in appropriate React component
- Consider adding CLI command for exportApiConfiguration if appropriate

### exportApiKeysSecure
**File:** `src/components/SynapseGateway.js:710`
**Module:** `src.components.SynapseGateway`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for exportApiKeysSecure
- Add UI button/form calling exportApiKeysSecure in appropriate React component
- Consider adding CLI command for exportApiKeysSecure if appropriate

### constructor
**File:** `src/core/SpriteEngine.js:17`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for constructor in CoreInterface.js
- Add core management CLI command for constructor

### catch
**File:** `src/core/SpriteEngine.js:181`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### constructor
**File:** `src/core/SpriteEngine.js:221`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for constructor in CoreInterface.js
- Add core management CLI command for constructor

### catch
**File:** `src/core/SpriteEngine.js:285`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:333`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:357`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:378`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:399`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:433`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### shutdown
**File:** `src/core/SpriteEngine.js:515`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for shutdown in CoreInterface.js
- Add core management CLI command for shutdown

### constructor
**File:** `src/core/SpriteEngine.js:524`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for constructor in CoreInterface.js
- Add core management CLI command for constructor

### initialize
**File:** `src/core/SpriteEngine.js:620`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation

**Recommendations:**
- Add Core interface control for initialize in CoreInterface.js

### catch
**File:** `src/core/SpriteEngine.js:648`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:722`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:735`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:782`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:956`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:1015`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:1060`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:1116`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:1192`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:1235`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:1267`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:1292`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:1315`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### auditLog
**File:** `src/core/SpriteEngine.js:1342`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for auditLog in CoreInterface.js
- Add core management CLI command for auditLog

### catch
**File:** `src/core/SpriteEngine.js:1362`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### catch
**File:** `src/core/SpriteEngine.js:1394`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for catch in CoreInterface.js
- Add core management CLI command for catch

### shutdown
**File:** `src/core/SpriteEngine.js:1543`
**Module:** `src.core.SpriteEngine`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add Core interface control for shutdown in CoreInterface.js
- Add core management CLI command for shutdown

### catch
**File:** `src/personas/alden/AldenInterface.js:50`
**Module:** `src.personas.alden.AldenInterface`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `src/personas/alden/AldenInterface.js:315`
**Module:** `src.personas.alden.AldenInterface`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### callExternal
**File:** `src/utils/APIManager.js:714`
**Module:** `src.utils.APIManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for callExternal
- Consider adding UI control for callExternal if user-facing
- Consider adding CLI command for callExternal if appropriate

### sendToModule
**File:** `src/utils/APIManager.js:715`
**Module:** `src.utils.APIManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for sendToModule
- Consider adding UI control for sendToModule if user-facing
- Consider adding CLI command for sendToModule if appropriate

### emit
**File:** `src/utils/APIManager.js:716`
**Module:** `src.utils.APIManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for emit
- Consider adding UI control for emit if user-facing
- Consider adding CLI command for emit if appropriate

### getServices
**File:** `src/utils/APIManager.js:719`
**Module:** `src.utils.APIManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getServices
- Consider adding UI control for getServices if user-facing
- Consider adding CLI command for getServices if appropriate

### getEndpoints
**File:** `src/utils/APIManager.js:720`
**Module:** `src.utils.APIManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getEndpoints
- Consider adding UI control for getEndpoints if user-facing
- Consider adding CLI command for getEndpoints if appropriate

### getAPIStats
**File:** `src/utils/APIManager.js:721`
**Module:** `src.utils.APIManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getAPIStats
- Add UI button/form calling getAPIStats in appropriate React component
- Consider adding CLI command for getAPIStats if appropriate

### authenticate
**File:** `src/utils/AuthenticationManager.js:770`
**Module:** `src.utils.AuthenticationManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for authenticate
- Consider adding UI control for authenticate if user-facing
- Consider adding CLI command for authenticate if appropriate

### logout
**File:** `src/utils/AuthenticationManager.js:771`
**Module:** `src.utils.AuthenticationManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for logout
- Consider adding UI control for logout if user-facing
- Consider adding CLI command for logout if appropriate

### hasPermission
**File:** `src/utils/AuthenticationManager.js:772`
**Module:** `src.utils.AuthenticationManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for hasPermission
- Consider adding UI control for hasPermission if user-facing
- Consider adding CLI command for hasPermission if appropriate

### checkPermission
**File:** `src/utils/AuthenticationManager.js:773`
**Module:** `src.utils.AuthenticationManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for checkPermission
- Consider adding UI control for checkPermission if user-facing
- Consider adding CLI command for checkPermission if appropriate

### isAuthenticated
**File:** `src/utils/AuthenticationManager.js:774`
**Module:** `src.utils.AuthenticationManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for isAuthenticated
- Consider adding UI control for isAuthenticated if user-facing
- Consider adding CLI command for isAuthenticated if appropriate

### getCurrentUser
**File:** `src/utils/AuthenticationManager.js:775`
**Module:** `src.utils.AuthenticationManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getCurrentUser
- Consider adding UI control for getCurrentUser if user-facing
- Consider adding CLI command for getCurrentUser if appropriate

### getAuthState
**File:** `src/utils/AuthenticationManager.js:776`
**Module:** `src.utils.AuthenticationManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getAuthState
- Consider adding UI control for getAuthState if user-facing
- Consider adding CLI command for getAuthState if appropriate

### validateSession
**File:** `src/utils/AuthenticationManager.js:777`
**Module:** `src.utils.AuthenticationManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for validateSession
- Consider adding UI control for validateSession if user-facing
- Consider adding CLI command for validateSession if appropriate

### getAuthStats
**File:** `src/utils/AuthenticationManager.js:778`
**Module:** `src.utils.AuthenticationManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getAuthStats
- Consider adding UI control for getAuthStats if user-facing
- Consider adding CLI command for getAuthStats if appropriate

### exportConfiguration
**File:** `src/utils/ConfigManager.js:610`
**Module:** `src.utils.ConfigManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for exportConfiguration
- Consider adding UI control for exportConfiguration if user-facing
- Consider adding CLI command for exportConfiguration if appropriate

### watch
**File:** `src/utils/ConfigManager.js:762`
**Module:** `src.utils.ConfigManager`
**Missing:** test, ui_invocation

**Recommendations:**
- Add Jest unit test for watch
- Consider adding UI control for watch if user-facing

### getEnvironment
**File:** `src/utils/ConfigManager.js:763`
**Module:** `src.utils.ConfigManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getEnvironment
- Consider adding UI control for getEnvironment if user-facing
- Consider adding CLI command for getEnvironment if appropriate

### isProduction
**File:** `src/utils/ConfigManager.js:764`
**Module:** `src.utils.ConfigManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for isProduction
- Consider adding UI control for isProduction if user-facing
- Consider adding CLI command for isProduction if appropriate

### isDevelopment
**File:** `src/utils/ConfigManager.js:765`
**Module:** `src.utils.ConfigManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for isDevelopment
- Consider adding UI control for isDevelopment if user-facing
- Consider adding CLI command for isDevelopment if appropriate

### exportConfig
**File:** `src/utils/ConfigManager.js:766`
**Module:** `src.utils.ConfigManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for exportConfig
- Consider adding UI control for exportConfig if user-facing
- Consider adding CLI command for exportConfig if appropriate

### importConfig
**File:** `src/utils/ConfigManager.js:768`
**Module:** `src.utils.ConfigManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for importConfig
- Consider adding UI control for importConfig if user-facing
- Consider adding CLI command for importConfig if appropriate

### getConfigStats
**File:** `src/utils/ConfigManager.js:769`
**Module:** `src.utils.ConfigManager`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getConfigStats
- Consider adding UI control for getConfigStats if user-facing
- Consider adding CLI command for getConfigStats if appropriate

### exportMetrics
**File:** `src/utils/DelegationMetrics.js:569`
**Module:** `src.utils.DelegationMetrics`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for exportMetrics
- Consider adding UI control for exportMetrics if user-facing
- Consider adding CLI command for exportMetrics if appropriate

### exportErrorHistory
**File:** `src/utils/ErrorHandler.js:614`
**Module:** `src.utils.ErrorHandler`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for exportErrorHistory
- Consider adding UI control for exportErrorHistory if user-facing
- Consider adding CLI command for exportErrorHistory if appropriate

### handleError
**File:** `src/utils/ErrorHandler.js:632`
**Module:** `src.utils.ErrorHandler`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for handleError
- Consider adding UI control for handleError if user-facing
- Consider adding CLI command for handleError if appropriate

### getErrorHistory
**File:** `src/utils/ErrorHandler.js:633`
**Module:** `src.utils.ErrorHandler`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getErrorHistory
- Consider adding UI control for getErrorHistory if user-facing
- Consider adding CLI command for getErrorHistory if appropriate

### getErrorStats
**File:** `src/utils/ErrorHandler.js:634`
**Module:** `src.utils.ErrorHandler`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getErrorStats
- Consider adding UI control for getErrorStats if user-facing
- Consider adding CLI command for getErrorStats if appropriate

### exportErrorHistory
**File:** `src/utils/ErrorHandler.js:635`
**Module:** `src.utils.ErrorHandler`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for exportErrorHistory
- Consider adding UI control for exportErrorHistory if user-facing
- Consider adding CLI command for exportErrorHistory if appropriate

### getSystemHealth
**File:** `src/utils/HealthMonitor.js:803`
**Module:** `src.utils.HealthMonitor`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getSystemHealth
- Consider adding UI control for getSystemHealth if user-facing
- Consider adding CLI command for getSystemHealth if appropriate

### getModuleHealth
**File:** `src/utils/HealthMonitor.js:804`
**Module:** `src.utils.HealthMonitor`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getModuleHealth
- Consider adding UI control for getModuleHealth if user-facing
- Consider adding CLI command for getModuleHealth if appropriate

### recordMetric
**File:** `src/utils/HealthMonitor.js:805`
**Module:** `src.utils.HealthMonitor`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for recordMetric
- Consider adding UI control for recordMetric if user-facing
- Consider adding CLI command for recordMetric if appropriate

### createAlert
**File:** `src/utils/HealthMonitor.js:806`
**Module:** `src.utils.HealthMonitor`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for createAlert
- Consider adding UI control for createAlert if user-facing
- Consider adding CLI command for createAlert if appropriate

### getDiagnosticReport
**File:** `src/utils/HealthMonitor.js:807`
**Module:** `src.utils.HealthMonitor`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getDiagnosticReport
- Consider adding UI control for getDiagnosticReport if user-facing
- Consider adding CLI command for getDiagnosticReport if appropriate

### getHealthStats
**File:** `src/utils/HealthMonitor.js:808`
**Module:** `src.utils.HealthMonitor`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getHealthStats
- Consider adding UI control for getHealthStats if user-facing
- Consider adding CLI command for getHealthStats if appropriate

### acknowledgeAlert
**File:** `src/utils/HealthMonitor.js:809`
**Module:** `src.utils.HealthMonitor`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for acknowledgeAlert
- Consider adding UI control for acknowledgeAlert if user-facing
- Consider adding CLI command for acknowledgeAlert if appropriate

### exportLogs
**File:** `src/utils/SystemLogger.js:265`
**Module:** `src.utils.SystemLogger`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for exportLogs
- Consider adding UI control for exportLogs if user-facing
- Consider adding CLI command for exportLogs if appropriate

### debug
**File:** `src/utils/SystemLogger.js:371`
**Module:** `src.utils.SystemLogger`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for debug if user-facing
- Consider adding CLI command for debug if appropriate

### userAction
**File:** `src/utils/SystemLogger.js:376`
**Module:** `src.utils.SystemLogger`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for userAction
- Consider adding UI control for userAction if user-facing
- Consider adding CLI command for userAction if appropriate

### apiCall
**File:** `src/utils/SystemLogger.js:377`
**Module:** `src.utils.SystemLogger`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Add UI button/form calling apiCall in appropriate React component
- Consider adding CLI command for apiCall if appropriate

### agentAction
**File:** `src/utils/SystemLogger.js:379`
**Module:** `src.utils.SystemLogger`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for agentAction
- Consider adding UI control for agentAction if user-facing
- Consider adding CLI command for agentAction if appropriate

### securityEvent
**File:** `src/utils/SystemLogger.js:381`
**Module:** `src.utils.SystemLogger`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for securityEvent
- Consider adding UI control for securityEvent if user-facing
- Consider adding CLI command for securityEvent if appropriate

### createContext
**File:** `src/utils/SystemLogger.js:385`
**Module:** `src.utils.SystemLogger`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for createContext
- Consider adding UI control for createContext if user-facing
- Consider adding CLI command for createContext if appropriate

### withContext
**File:** `src/utils/SystemLogger.js:387`
**Module:** `src.utils.SystemLogger`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for withContext
- Consider adding UI control for withContext if user-facing
- Consider adding CLI command for withContext if appropriate

### getLogs
**File:** `src/utils/SystemLogger.js:389`
**Module:** `src.utils.SystemLogger`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getLogs
- Consider adding UI control for getLogs if user-facing
- Consider adding CLI command for getLogs if appropriate

### exportLogs
**File:** `src/utils/SystemLogger.js:390`
**Module:** `src.utils.SystemLogger`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for exportLogs
- Consider adding UI control for exportLogs if user-facing
- Consider adding CLI command for exportLogs if appropriate

### getLogStats
**File:** `src/utils/SystemLogger.js:391`
**Module:** `src.utils.SystemLogger`
**Missing:** test, ui_invocation, cli_invocation

**Recommendations:**
- Add Jest unit test for getLogStats
- Consider adding UI control for getLogStats if user-facing
- Consider adding CLI command for getLogStats if appropriate

### catch
**File:** `ipcHandlers/core.ts:8`
**Module:** `ipcHandlers.core`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/core.ts:27`
**Module:** `ipcHandlers.core`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/core.ts:43`
**Module:** `ipcHandlers.core`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/core.ts:59`
**Module:** `ipcHandlers.core`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/core.ts:75`
**Module:** `ipcHandlers.core`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/core.ts:91`
**Module:** `ipcHandlers.core`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/general.ts:24`
**Module:** `ipcHandlers.general`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/general.ts:33`
**Module:** `ipcHandlers.general`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/general.ts:62`
**Module:** `ipcHandlers.general`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/general.ts:82`
**Module:** `ipcHandlers.general`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/synapse.ts:8`
**Module:** `ipcHandlers.synapse`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/synapse.ts:27`
**Module:** `ipcHandlers.synapse`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/synapse.ts:43`
**Module:** `ipcHandlers.synapse`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/vault.ts:8`
**Module:** `ipcHandlers.vault`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/vault.ts:27`
**Module:** `ipcHandlers.vault`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `ipcHandlers/vault.ts:43`
**Module:** `ipcHandlers.vault`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### constructor
**File:** `services/metrics.ts:12`
**Module:** `services.metrics`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for constructor if user-facing
- Consider adding CLI command for constructor if appropriate

### constructor
**File:** `services/metrics.ts:62`
**Module:** `services.metrics`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for constructor if user-facing
- Consider adding CLI command for constructor if appropriate

### catch
**File:** `services/metrics.ts:162`
**Module:** `services.metrics`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `services/metrics.ts:184`
**Module:** `services.metrics`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `services/metrics.ts:212`
**Module:** `services.metrics`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `services/metrics.ts:254`
**Module:** `services.metrics`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `services/protocolHandler.ts:66`
**Module:** `services.protocolHandler`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `services/protocolHandler.ts:72`
**Module:** `services.protocolHandler`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### replace
**File:** `services/pythonBridge.ts:16`
**Module:** `services.pythonBridge`
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for replace if user-facing

### catch
**File:** `services/pythonBridge.ts:78`
**Module:** `services.pythonBridge`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### sendToPython
**File:** `services/pythonBridge.ts:118`
**Module:** `services.pythonBridge`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for sendToPython if user-facing
- Consider adding CLI command for sendToPython if appropriate

### sendToPython
**File:** `services/pythonBridge.ts:118`
**Module:** `services.pythonBridge`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for sendToPython if user-facing
- Consider adding CLI command for sendToPython if appropriate

### catch
**File:** `services/pythonBridge.ts:141`
**Module:** `services.pythonBridge`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `services/staticServer.ts:126`
**Module:** `services.staticServer`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### constructor
**File:** `services/memory-sync/conflict-policies.js:43`
**Module:** `services.memory-sync.conflict-policies`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for constructor if user-facing
- Consider adding CLI command for constructor if appropriate

### catch
**File:** `services/memory-sync/conflict-policies.js:450`
**Module:** `services.memory-sync.conflict-policies`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### constructor
**File:** `services/memory-sync/index.js:166`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for constructor if user-facing
- Consider adding CLI command for constructor if appropriate

### initialize
**File:** `services/memory-sync/index.js:191`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for initialize if user-facing

### catch
**File:** `services/memory-sync/index.js:229`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `services/memory-sync/index.js:282`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `services/memory-sync/index.js:297`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `services/memory-sync/index.js:312`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `services/memory-sync/index.js:358`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### handleMemorySync
**File:** `services/memory-sync/index.js:365`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for handleMemorySync if user-facing
- Consider adding CLI command for handleMemorySync if appropriate

### catch
**File:** `services/memory-sync/index.js:426`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### handleSyncConflict
**File:** `services/memory-sync/index.js:442`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for handleSyncConflict if user-facing
- Consider adding CLI command for handleSyncConflict if appropriate

### catch
**File:** `services/memory-sync/index.js:575`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### resolveByAgentPriority
**File:** `services/memory-sync/index.js:584`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for resolveByAgentPriority if user-facing
- Consider adding CLI command for resolveByAgentPriority if appropriate

### resolveByTimestamp
**File:** `services/memory-sync/index.js:608`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for resolveByTimestamp if user-facing
- Consider adding CLI command for resolveByTimestamp if appropriate

### processSyncOperation
**File:** `services/memory-sync/index.js:714`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for processSyncOperation if user-facing
- Add CLI command wrapper for processSyncOperation

### acquireMemoryLock
**File:** `services/memory-sync/index.js:738`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for acquireMemoryLock if user-facing
- Consider adding CLI command for acquireMemoryLock if appropriate

### catch
**File:** `services/memory-sync/index.js:757`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### releaseMemoryLock
**File:** `services/memory-sync/index.js:763`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for releaseMemoryLock if user-facing
- Consider adding CLI command for releaseMemoryLock if appropriate

### catch
**File:** `services/memory-sync/index.js:769`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### checkExistingSync
**File:** `services/memory-sync/index.js:774`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for checkExistingSync if user-facing
- Consider adding CLI command for checkExistingSync if appropriate

### catch
**File:** `services/memory-sync/index.js:830`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### catch
**File:** `services/memory-sync/index.js:892`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### shutdown
**File:** `services/memory-sync/index.js:933`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for shutdown if user-facing
- Consider adding CLI command for shutdown if appropriate

### catch
**File:** `services/memory-sync/index.js:948`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation, cli_invocation

**Recommendations:**
- Consider adding UI control for catch if user-facing
- Consider adding CLI command for catch if appropriate

### start
**File:** `services/memory-sync/index.js:953`
**Module:** `services.memory-sync.index`
**Missing:** ui_invocation

**Recommendations:**
- Consider adding UI control for start if user-facing

### GET /api/v1/alden/status
**File:** `src/api/alden_api.py:289`
**Module:** `src.api.alden_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/v1/alden/status in appropriate React component

### GET /api/v1/alden/health
**File:** `src/api/alden_api.py:329`
**Module:** `src.api.alden_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/v1/alden/health in appropriate React component

### GET /api/health
**File:** `src/api/core_api.py:276`
**Module:** `src.api.core_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/health in appropriate React component

### GET /api/agents/<agent_id>
**File:** `src/api/core_api.py:301`
**Module:** `src.api.core_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/agents/<agent_id> in appropriate React component

### POST /api/sessions
**File:** `src/api/core_api.py:453`
**Module:** `src.api.core_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling POST /api/sessions in appropriate React component

### GET /api/sessions/<session_id>
**File:** `src/api/core_api.py:479`
**Module:** `src.api.core_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/sessions/<session_id> in appropriate React component

### GET /api/system/metrics
**File:** `src/api/core_api.py:558`
**Module:** `src.api.core_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/system/metrics in appropriate React component

### GET /health
**File:** `src/api/enhanced_core_api.py:360`
**Module:** `src.api.enhanced_core_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /health in appropriate React component

### GET /chat
**File:** `src/api/kimi_k2_api.py:107`
**Module:** `src.api.kimi_k2_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /chat in appropriate React component

### GET /health
**File:** `src/api/kimi_k2_api.py:292`
**Module:** `src.api.kimi_k2_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /health in appropriate React component

### GET /metrics
**File:** `src/api/kimi_k2_api.py:401`
**Module:** `src.api.kimi_k2_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /metrics in appropriate React component

### GET /validate-license
**File:** `src/api/license_validation.py:170`
**Module:** `src.api.license_validation`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /validate-license in appropriate React component

### GET /record-usage
**File:** `src/api/license_validation.py:240`
**Module:** `src.api.license_validation`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /record-usage in appropriate React component

### GET /start-trial
**File:** `src/api/license_validation.py:276`
**Module:** `src.api.license_validation`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /start-trial in appropriate React component

### GET /api/health
**File:** `src/api/local_llm_api.py:261`
**Module:** `src.api.local_llm_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/health in appropriate React component

### GET /api/status
**File:** `src/api/local_llm_api.py:273`
**Module:** `src.api.local_llm_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/status in appropriate React component

### POST /api/chat
**File:** `src/api/local_llm_api.py:365`
**Module:** `src.api.local_llm_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling POST /api/chat in appropriate React component

### POST /api/test
**File:** `src/api/local_llm_api.py:456`
**Module:** `src.api.local_llm_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling POST /api/test in appropriate React component

### GET /api/metrics
**File:** `src/api/local_llm_api.py:520`
**Module:** `src.api.local_llm_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/metrics in appropriate React component

### GET /api/mimic/persona/generate
**File:** `src/api/mimic_api.py:202`
**Module:** `src.api.mimic_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/mimic/persona/generate in appropriate React component

### GET /api/mimic/persona/{persona_id}/performance
**File:** `src/api/mimic_api.py:250`
**Module:** `src.api.mimic_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/mimic/persona/{persona_id}/performance in appropriate React component

### GET /api/mimic/persona/{persona_id}/analytics
**File:** `src/api/mimic_api.py:291`
**Module:** `src.api.mimic_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/mimic/persona/{persona_id}/analytics in appropriate React component

### GET /api/mimic/persona/fork
**File:** `src/api/mimic_api.py:320`
**Module:** `src.api.mimic_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/mimic/persona/fork in appropriate React component

### GET /api/mimic/persona/merge
**File:** `src/api/mimic_api.py:370`
**Module:** `src.api.mimic_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/mimic/persona/merge in appropriate React component

### GET /api/mimic/persona/{persona_id}/plugin
**File:** `src/api/mimic_api.py:411`
**Module:** `src.api.mimic_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/mimic/persona/{persona_id}/plugin in appropriate React component

### GET /api/mimic/persona/{persona_id}/tier
**File:** `src/api/mimic_api.py:565`
**Module:** `src.api.mimic_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/mimic/persona/{persona_id}/tier in appropriate React component

### GET /api/mimic/health
**File:** `src/api/mimic_api.py:701`
**Module:** `src.api.mimic_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/mimic/health in appropriate React component

### GET /api/sentry/health
**File:** `src/api/sentry_api.py:403`
**Module:** `src.api.sentry_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/sentry/health in appropriate React component

### GET /api/health
**File:** `src/api/settings_api.py:378`
**Module:** `src.api.settings_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/health in appropriate React component

### POST /api/test/<service>
**File:** `src/api/simple_backend.py:160`
**Module:** `src.api.simple_backend`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling POST /api/test/<service> in appropriate React component

### GET /api/status
**File:** `src/api/simple_backend.py:182`
**Module:** `src.api.simple_backend`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/status in appropriate React component

### GET /api/superclaude/status
**File:** `src/api/superclaude_api.py:265`
**Module:** `src.api.superclaude_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/superclaude/status in appropriate React component

### POST /api/superclaude/session
**File:** `src/api/superclaude_api.py:290`
**Module:** `src.api.superclaude_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling POST /api/superclaude/session in appropriate React component

### POST /api/superclaude/chat
**File:** `src/api/superclaude_api.py:335`
**Module:** `src.api.superclaude_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling POST /api/superclaude/chat in appropriate React component

### GET /api/vault/health
**File:** `src/api/system_health.py:52`
**Module:** `src.api.system_health`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/vault/health in appropriate React component

### GET /
**File:** `src/api/task_templates.py:211`
**Module:** `src.api.task_templates`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET / in appropriate React component

### GET /
**File:** `src/api/task_templates.py:279`
**Module:** `src.api.task_templates`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET / in appropriate React component

### GET /audit
**File:** `src/api/task_templates.py:409`
**Module:** `src.api.task_templates`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /audit in appropriate React component

### GET /api/vault/health
**File:** `src/api/vault_api.py:59`
**Module:** `src.api.vault_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/vault/health in appropriate React component

### GET /api/vault/memories/<memory_id>
**File:** `src/api/vault_api.py:190`
**Module:** `src.api.vault_api`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /api/vault/memories/<memory_id> in appropriate React component

### GET /query
**File:** `src/backend/alden_backend.py:512`
**Module:** `src.backend.alden_backend`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /query in appropriate React component

### GET /health
**File:** `src/backend/alden_backend.py:522`
**Module:** `src.backend.alden_backend`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /health in appropriate React component

### GET /status
**File:** `src/backend/alden_backend.py:531`
**Module:** `src.backend.alden_backend`
**Missing:** ui_invocation

**Recommendations:**
- Add UI button/form calling GET /status in appropriate React component

## Coverage Gaps by Module

### ipcHandlers.core
**Gaps:** 11

- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `IPC /ipc/core-create-session` (critical) - Missing: test, ui_invocation
- `IPC /ipc/core-get-session` (critical) - Missing: test, ui_invocation
- `IPC /ipc/core-add-participant` (critical) - Missing: test, ui_invocation
- `IPC /ipc/core-start-turn-taking` (critical) - Missing: test, ui_invocation
- `IPC /ipc/core-advance-turn` (critical) - Missing: test, ui_invocation

### ipcHandlers.general
**Gaps:** 11

- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `IPC /ipc/get-app-version` (critical) - Missing: ui_invocation
- `IPC /ipc/get-app-path` (critical) - Missing: ui_invocation
- `IPC /ipc/get-resource-path` (critical) - Missing: test, ui_invocation
- `IPC /ipc/read-documentation` (critical) - Missing: test, ui_invocation
- `IPC /ipc/open-external` (critical) - Missing: test, ui_invocation
- `IPC /ipc/voice-command` (critical) - Missing: test, ui_invocation
- `IPC /ipc/accessibility-toggle` (critical) - Missing: test, ui_invocation

### ipcHandlers.synapse
**Gaps:** 5

- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `IPC /ipc/synapse-execute-plugin` (critical) - Missing: test, ui_invocation
- `IPC /ipc/synapse-list-plugins` (critical) - Missing: test, ui_invocation

### ipcHandlers.vault
**Gaps:** 5

- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `IPC /ipc/vault-get-persona-memory` (critical) - Missing: test, ui_invocation
- `IPC /ipc/vault-update-persona-memory` (critical) - Missing: test, ui_invocation

### scripts.alpha_readiness_test
**Gaps:** 8

- `main` (medium) - Missing: ui_invocation
- `validate_vault_manager_health` (medium) - Missing: ui_invocation
- `validate_database_constraints` (medium) - Missing: ui_invocation
- `validate_rag_cag_pipeline` (medium) - Missing: ui_invocation
- `validate_handoff_continuity` (medium) - Missing: ui_invocation
- `validate_config_alignment` (medium) - Missing: ui_invocation
- `run_comprehensive_validation` (high) - Missing: ui_invocation
- `print_summary` (medium) - Missing: ui_invocation

### scripts.function_inventory
**Gaps:** 2

- `main` (medium) - Missing: ui_invocation
- `scan_repository` (high) - Missing: test, ui_invocation

### scripts.quick_alpha_test
**Gaps:** 1

- `main` (medium) - Missing: ui_invocation

### scripts.run_performance_tests
**Gaps:** 8

- `main` (medium) - Missing: ui_invocation
- `run_smoke_tests` (critical) - Missing: test, ui_invocation
- `run_load_tests` (critical) - Missing: test, ui_invocation
- `validate_spec2_components` (high) - Missing: test, ui_invocation
- `run_installer_tests` (critical) - Missing: test, ui_invocation
- `calculate_overall_performance_grade` (high) - Missing: test, ui_invocation
- `generate_comprehensive_report` (high) - Missing: test, ui_invocation
- `print_summary` (medium) - Missing: ui_invocation

### scripts.setup_databases
**Gaps:** 2

- `load_config` (high) - Missing: test, ui_invocation
- `main` (medium) - Missing: ui_invocation

### scripts.validate_installer
**Gaps:** 7

- `calculate_file_hash` (high) - Missing: test, ui_invocation
- `validate_spec2_components` (high) - Missing: test, ui_invocation
- `validate_assets` (high) - Missing: test, ui_invocation
- `validate_tauri_config` (high) - Missing: test, ui_invocation
- `validate_package_json` (high) - Missing: test, ui_invocation
- `check_build_artifacts` (high) - Missing: test, ui_invocation
- `generate_validation_report` (high) - Missing: test, ui_invocation

### scripts.vault_rotation_cli
**Gaps:** 13

- `cli` (medium) - Missing: ui_invocation
- `get_rotation_manager` (critical) - Missing: test, ui_invocation
- `status` (medium) - Missing: ui_invocation
- `rotate` (medium) - Missing: ui_invocation
- `history` (medium) - Missing: ui_invocation
- `rollback` (medium) - Missing: ui_invocation
- `versions` (medium) - Missing: ui_invocation
- `verify` (medium) - Missing: ui_invocation
- `policy` (medium) - Missing: ui_invocation
- `metrics` (medium) - Missing: ui_invocation
- `backup` (medium) - Missing: ui_invocation
- `monitor` (medium) - Missing: ui_invocation
- `show_status` (high) - Missing: test, ui_invocation

### scripts.verify_env
**Gaps:** 13

- `main` (medium) - Missing: ui_invocation
- `check_file_existence` (high) - Missing: test, ui_invocation
- `parse_env_file` (high) - Missing: test, ui_invocation
- `validate_variable_formats` (high) - Missing: test, ui_invocation
- `check_variable_completeness` (high) - Missing: test, ui_invocation
- `validate_with_loader` (high) - Missing: test, ui_invocation
- `check_security_issues` (high) - Missing: test, ui_invocation
- `load_config_schema` (high) - Missing: test, ui_invocation
- `validate_config_files` (high) - Missing: test, ui_invocation
- `validate_cross_service_config_alignment` (high) - Missing: test, ui_invocation
- `validate_required_env_vars_strict` (high) - Missing: test, ui_invocation
- `run_verification` (critical) - Missing: test, ui_invocation
- `print_results` (high) - Missing: test, ui_invocation

### services.memory-sync.conflict-policies
**Gaps:** 20

- `constructor` (high) - Missing: ui_invocation, cli_invocation
- `resolveConflict` (critical) - Missing: test, ui_invocation, cli_invocation
- `applyResolutionPolicies` (critical) - Missing: test, ui_invocation, cli_invocation
- `securityOverridePolicy` (critical) - Missing: test, ui_invocation, cli_invocation
- `emergencyTagPolicy` (critical) - Missing: test, ui_invocation, cli_invocation
- `agentPriorityPolicy` (critical) - Missing: test, ui_invocation, cli_invocation
- `customTagPolicy` (critical) - Missing: test, ui_invocation, cli_invocation
- `getHighestTagPriority` (critical) - Missing: test, ui_invocation, cli_invocation
- `recencyBiasPolicy` (critical) - Missing: test, ui_invocation, cli_invocation
- `timestampPolicy` (critical) - Missing: test, ui_invocation, cli_invocation
- `weightedImportancePolicy` (critical) - Missing: test, ui_invocation, cli_invocation
- `sessionContinuityPolicy` (critical) - Missing: test, ui_invocation, cli_invocation
- `contentMergePolicy` (critical) - Missing: test, ui_invocation, cli_invocation
- `stabilityFallbackPolicy` (critical) - Missing: test, ui_invocation, cli_invocation
- `canMergeContent` (critical) - Missing: test, ui_invocation, cli_invocation
- `mergeContent` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `calculateContentSimilarity` (critical) - Missing: test, ui_invocation, cli_invocation
- `updateResolutionStats` (critical) - Missing: test, ui_invocation, cli_invocation
- `getResolutionStats` (critical) - Missing: test, ui_invocation, cli_invocation

### services.memory-sync.index
**Gaps:** 39

- `getTagPriority` (critical) - Missing: test, ui_invocation, cli_invocation
- `calculateContentSimilarity` (critical) - Missing: test, ui_invocation, cli_invocation
- `calculateContentSimilarity` (critical) - Missing: test, ui_invocation, cli_invocation
- `mergeContent` (critical) - Missing: test, ui_invocation, cli_invocation
- `mergeContent` (critical) - Missing: test, ui_invocation, cli_invocation
- `constructor` (high) - Missing: ui_invocation, cli_invocation
- `initialize` (high) - Missing: ui_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `handleMemorySync` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `handleSyncConflict` (high) - Missing: ui_invocation, cli_invocation
- `determineResolutionStrategy` (critical) - Missing: test, ui_invocation, cli_invocation
- `attemptAutoResolution` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `resolveByAgentPriority` (high) - Missing: ui_invocation, cli_invocation
- `resolveByTimestamp` (high) - Missing: ui_invocation, cli_invocation
- `resolveByImportance` (critical) - Missing: test, ui_invocation, cli_invocation
- `mergeMemoryContent` (critical) - Missing: test, ui_invocation, cli_invocation
- `processSyncOperation` (high) - Missing: ui_invocation, cli_invocation
- `acquireMemoryLock` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `releaseMemoryLock` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `checkExistingSync` (high) - Missing: ui_invocation, cli_invocation
- `validateSyncData` (critical) - Missing: test, ui_invocation, cli_invocation
- `updateMetrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `getSyncStatus` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `forceMemorySync` (critical) - Missing: test, ui_invocation, cli_invocation
- `startConflictProcessor` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `processActiveConflicts` (critical) - Missing: test, ui_invocation, cli_invocation
- `shutdown` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `start` (high) - Missing: ui_invocation

### services.metrics
**Gaps:** 20

- `constructor` (high) - Missing: ui_invocation, cli_invocation
- `refill` (critical) - Missing: test, ui_invocation, cli_invocation
- `canMakeRequest` (critical) - Missing: test, ui_invocation, cli_invocation
- `addRequest` (critical) - Missing: test, ui_invocation, cli_invocation
- `getWaitTime` (critical) - Missing: test, ui_invocation, cli_invocation
- `getRemainingRequests` (critical) - Missing: test, ui_invocation, cli_invocation
- `constructor` (high) - Missing: ui_invocation, cli_invocation
- `startSession` (critical) - Missing: test, ui_invocation, cli_invocation
- `addDelegation` (critical) - Missing: test, ui_invocation, cli_invocation
- `endSession` (critical) - Missing: test, ui_invocation, cli_invocation
- `updateGlobalMetrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `queuePersistence` (critical) - Missing: test, ui_invocation, cli_invocation
- `processQueue` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `persistItem` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `compressOldData` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `getMetrics` (critical) - Missing: test, ui_invocation, cli_invocation

### services.protocolHandler
**Gaps:** 9

- `getCachedExists` (critical) - Missing: test, ui_invocation, cli_invocation
- `getCachedExists` (critical) - Missing: test, ui_invocation, cli_invocation
- `setCachedExists` (critical) - Missing: test, ui_invocation, cli_invocation
- `setCachedExists` (critical) - Missing: test, ui_invocation, cli_invocation
- `checkFileExists` (critical) - Missing: test, ui_invocation, cli_invocation
- `checkFileExists` (critical) - Missing: test, ui_invocation, cli_invocation
- `registerProtocolHandler` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation

### services.pythonBridge
**Gaps:** 14

- `validatePythonPath` (critical) - Missing: test, ui_invocation, cli_invocation
- `validatePythonPath` (critical) - Missing: test, ui_invocation, cli_invocation
- `replace` (high) - Missing: ui_invocation
- `startPythonBackend` (critical) - Missing: test, ui_invocation, cli_invocation
- `startPythonBackend` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `sendToPython` (high) - Missing: ui_invocation, cli_invocation
- `sendToPython` (high) - Missing: ui_invocation, cli_invocation
- `responseHandler` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `stopPythonBackend` (critical) - Missing: test, ui_invocation, cli_invocation
- `stopPythonBackend` (critical) - Missing: test, ui_invocation, cli_invocation
- `getPythonProcess` (critical) - Missing: test, ui_invocation, cli_invocation
- `getPythonProcess` (critical) - Missing: test, ui_invocation, cli_invocation

### services.staticServer
**Gaps:** 11

- `getCachedStat` (critical) - Missing: test, ui_invocation, cli_invocation
- `getCachedStat` (critical) - Missing: test, ui_invocation, cli_invocation
- `setCachedStat` (critical) - Missing: test, ui_invocation, cli_invocation
- `setCachedStat` (critical) - Missing: test, ui_invocation, cli_invocation
- `checkFileExists` (critical) - Missing: test, ui_invocation, cli_invocation
- `checkFileExists` (critical) - Missing: test, ui_invocation, cli_invocation
- `startStaticServer` (critical) - Missing: test, ui_invocation, cli_invocation
- `startStaticServer` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `stopStaticServer` (critical) - Missing: test, ui_invocation, cli_invocation
- `stopStaticServer` (critical) - Missing: test, ui_invocation, cli_invocation

### src.App
**Gaps:** 1

- `getModuleComponent` (high) - Missing: test, ui_invocation, cli_invocation

### src.api.alden_api
**Gaps:** 17

- `create_alden_api` (critical) - Missing: test, ui_invocation, cli_invocation
- `validate_message` (high) - Missing: test, ui_invocation, cli_invocation
- `run` (medium) - Missing: ui_invocation
- `send_message` (high) - Missing: test, ui_invocation, cli_invocation
- `update_trait` (critical) - Missing: test, ui_invocation, cli_invocation
- `add_correction` (high) - Missing: test, ui_invocation, cli_invocation
- `record_mood` (high) - Missing: test, ui_invocation, cli_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation
- `export_memory` (high) - Missing: test, ui_invocation, cli_invocation
- `health_check` (medium) - Missing: ui_invocation
- `GET /api/v1/alden/message` (critical) - Missing: test, ui_invocation
- `GET /api/v1/alden/traits/{trait_name}` (critical) - Missing: test, ui_invocation
- `GET /api/v1/alden/corrections` (critical) - Missing: test, ui_invocation
- `GET /api/v1/alden/mood` (critical) - Missing: test, ui_invocation
- `GET /api/v1/alden/status` (high) - Missing: ui_invocation
- `GET /api/v1/alden/memory/export` (critical) - Missing: test, ui_invocation
- `GET /api/v1/alden/health` (high) - Missing: ui_invocation

### src.api.claude_code_cli
**Gaps:** 15

- `initialize_claude_code_cli` (high) - Missing: test, ui_invocation, cli_invocation
- `is_available` (high) - Missing: test, ui_invocation, cli_invocation
- `get_version` (critical) - Missing: test, ui_invocation, cli_invocation
- `start_session` (high) - Missing: test, ui_invocation, cli_invocation
- `execute_command` (critical) - Missing: test, ui_invocation, cli_invocation
- `analyze_code` (high) - Missing: test, ui_invocation, cli_invocation
- `generate_code` (high) - Missing: test, ui_invocation, cli_invocation
- `refactor_code` (high) - Missing: test, ui_invocation, cli_invocation
- `explain_code` (high) - Missing: test, ui_invocation, cli_invocation
- `debug_code` (high) - Missing: test, ui_invocation, cli_invocation
- `get_session_history` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_current_session` (critical) - Missing: test, ui_invocation, cli_invocation
- `end_session` (high) - Missing: ui_invocation, cli_invocation
- `get_available_commands` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation

### src.api.core_api
**Gaps:** 46

- `update_agent_statuses` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_service_statuses` (critical) - Missing: test, ui_invocation, cli_invocation
- `initialize_mock_data` (high) - Missing: test, ui_invocation, cli_invocation
- `add_orchestration_log` (high) - Missing: test, ui_invocation, cli_invocation
- `health_check` (medium) - Missing: ui_invocation
- `get_agents` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_agent` (high) - Missing: ui_invocation
- `update_agent` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_services` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_service_health` (high) - Missing: test, ui_invocation, cli_invocation
- `get_projects` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_project` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_project` (critical) - Missing: test, ui_invocation, cli_invocation
- `start_project_orchestration` (high) - Missing: test, ui_invocation, cli_invocation
- `delegate_task` (high) - Missing: test, ui_invocation, cli_invocation
- `get_sessions` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_session` (high) - Missing: ui_invocation
- `get_session` (high) - Missing: ui_invocation
- `join_session` (high) - Missing: test, ui_invocation, cli_invocation
- `send_session_message` (high) - Missing: test, ui_invocation, cli_invocation
- `get_orchestration_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_orchestration_logs` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_system_metrics` (critical) - Missing: ui_invocation, cli_invocation
- `get_system_memory` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_system_health` (critical) - Missing: test, ui_invocation, cli_invocation
- `GET /api/health` (high) - Missing: ui_invocation
- `GET /api/agents` (critical) - Missing: test, ui_invocation
- `GET /api/agents/<agent_id>` (high) - Missing: ui_invocation
- `PUT /api/agents/<agent_id>` (critical) - Missing: test, ui_invocation
- `GET /api/services` (critical) - Missing: test, ui_invocation
- `GET /api/services/<service_id>/health` (critical) - Missing: test, ui_invocation
- `GET /api/projects` (critical) - Missing: test, ui_invocation
- `POST /api/projects` (critical) - Missing: test, ui_invocation
- `GET /api/projects/<project_id>` (critical) - Missing: test, ui_invocation
- `POST /api/projects/<project_id>/orchestrate` (critical) - Missing: test, ui_invocation
- `POST /api/projects/<project_id>/tasks/<task_id>/delegate` (critical) - Missing: test, ui_invocation
- `GET /api/sessions` (critical) - Missing: test, ui_invocation
- `POST /api/sessions` (high) - Missing: ui_invocation
- `GET /api/sessions/<session_id>` (high) - Missing: ui_invocation
- `POST /api/sessions/<session_id>/join` (critical) - Missing: test, ui_invocation
- `POST /api/sessions/<session_id>/message` (critical) - Missing: test, ui_invocation
- `GET /api/orchestration/status` (critical) - Missing: test, ui_invocation
- `GET /api/orchestration/logs` (critical) - Missing: test, ui_invocation
- `GET /api/system/metrics` (high) - Missing: ui_invocation
- `GET /api/system/memory` (critical) - Missing: test, ui_invocation
- `GET /api/system/health` (critical) - Missing: test, ui_invocation

### src.api.enhanced_core_api
**Gaps:** 26

- `get_enhanced_core` (critical) - Missing: test, ui_invocation, cli_invocation
- `authenticate_request` (high) - Missing: test, ui_invocation, cli_invocation
- `create_agentic_session` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_agentic_task` (critical) - Missing: test, ui_invocation, cli_invocation
- `delegate_task` (high) - Missing: test, ui_invocation, cli_invocation
- `get_agent_capabilities` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_workflow_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `control_workflow` (high) - Missing: test, ui_invocation, cli_invocation
- `get_enhanced_session_info` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_session_workflows` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_agent_delegations` (critical) - Missing: test, ui_invocation, cli_invocation
- `suggest_agent` (high) - Missing: test, ui_invocation, cli_invocation
- `health_check` (medium) - Missing: ui_invocation
- `startup_event` (high) - Missing: ui_invocation, cli_invocation
- `shutdown_event` (high) - Missing: ui_invocation, cli_invocation
- `GET /session/agentic` (critical) - Missing: test, ui_invocation
- `GET /task/agentic` (critical) - Missing: test, ui_invocation
- `GET /task/delegate` (critical) - Missing: test, ui_invocation
- `GET /agents/capabilities` (critical) - Missing: test, ui_invocation
- `GET /workflows/status` (critical) - Missing: test, ui_invocation
- `GET /workflow/control` (critical) - Missing: test, ui_invocation
- `GET /session/{session_id}/enhanced` (critical) - Missing: test, ui_invocation
- `GET /session/{session_id}/workflows` (critical) - Missing: test, ui_invocation
- `GET /agents/{agent_id}/delegations` (critical) - Missing: test, ui_invocation
- `GET /agents/suggest` (critical) - Missing: test, ui_invocation
- `GET /health` (high) - Missing: ui_invocation

### src.api.external_agent_api
**Gaps:** 22

- `list_external_agents` (high) - Missing: test, ui_invocation, cli_invocation
- `get_agent_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_agent_action` (critical) - Missing: test, ui_invocation, cli_invocation
- `generate_with_agent` (high) - Missing: test, ui_invocation, cli_invocation
- `write_file_with_agent` (high) - Missing: test, ui_invocation, cli_invocation
- `read_file_with_agent` (high) - Missing: test, ui_invocation, cli_invocation
- `list_files_with_agent` (high) - Missing: test, ui_invocation, cli_invocation
- `get_circuit_breakers_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `reset_circuit_breaker` (high) - Missing: test, ui_invocation, cli_invocation
- `reset_all_circuit_breakers` (high) - Missing: test, ui_invocation, cli_invocation
- `get_agent_instance` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_agent_request` (critical) - Missing: test, ui_invocation, cli_invocation
- `GET /api/external-agents` (critical) - Missing: test, ui_invocation
- `GET /api/external-agents/<agent_id>/status` (critical) - Missing: test, ui_invocation
- `POST /api/external-agents/<agent_id>/execute` (critical) - Missing: test, ui_invocation
- `POST /api/external-agents/<agent_id>/generate` (critical) - Missing: test, ui_invocation
- `POST /api/external-agents/<agent_id>/files/write` (critical) - Missing: test, ui_invocation
- `POST /api/external-agents/<agent_id>/files/read` (critical) - Missing: test, ui_invocation
- `GET /api/external-agents/<agent_id>/files/list` (critical) - Missing: test, ui_invocation
- `GET /api/external-agents/circuit-breakers/status` (critical) - Missing: test, ui_invocation
- `POST /api/external-agents/circuit-breakers/<service_name>/reset` (critical) - Missing: test, ui_invocation
- `POST /api/external-agents/circuit-breakers/reset-all` (critical) - Missing: test, ui_invocation

### src.api.initialize_services
**Gaps:** 1

- `main` (medium) - Missing: ui_invocation

### src.api.kimi_k2_api
**Gaps:** 21

- `get_kimi_k2_backend` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_rate_limit` (high) - Missing: test, ui_invocation, cli_invocation
- `authenticate_request` (high) - Missing: test, ui_invocation, cli_invocation
- `chat` (high) - Missing: ui_invocation, cli_invocation
- `agentic_workflow` (high) - Missing: test, ui_invocation, cli_invocation
- `long_context_processing` (high) - Missing: test, ui_invocation, cli_invocation
- `health_check` (medium) - Missing: ui_invocation
- `get_stats` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_capabilities` (critical) - Missing: test, ui_invocation, cli_invocation
- `estimate_cost` (high) - Missing: test, ui_invocation, cli_invocation
- `get_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `startup_event` (high) - Missing: ui_invocation, cli_invocation
- `shutdown_event` (high) - Missing: ui_invocation, cli_invocation
- `GET /chat` (high) - Missing: ui_invocation
- `GET /agentic` (critical) - Missing: test, ui_invocation
- `GET /long-context` (critical) - Missing: test, ui_invocation
- `GET /health` (high) - Missing: ui_invocation
- `GET /stats` (critical) - Missing: test, ui_invocation
- `GET /capabilities` (critical) - Missing: test, ui_invocation
- `GET /estimate-cost` (critical) - Missing: test, ui_invocation
- `GET /metrics` (high) - Missing: ui_invocation

### src.api.license_validation
**Gaps:** 16

- `get_current_user` (critical) - Missing: test, ui_invocation, cli_invocation
- `generate_license_hash` (high) - Missing: test, ui_invocation, cli_invocation
- `validate_license_format` (high) - Missing: test, ui_invocation, cli_invocation
- `get_license_usage` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_license_usage` (critical) - Missing: test, ui_invocation, cli_invocation
- `validate_steve_august_license` (high) - Missing: test, ui_invocation, cli_invocation
- `validate_template_license` (high) - Missing: test, ui_invocation, cli_invocation
- `record_template_usage` (high) - Missing: test, ui_invocation, cli_invocation
- `start_template_trial` (high) - Missing: test, ui_invocation, cli_invocation
- `get_template_license_info` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_user_licenses` (critical) - Missing: test, ui_invocation, cli_invocation
- `GET /validate-license` (high) - Missing: ui_invocation
- `GET /record-usage` (high) - Missing: ui_invocation
- `GET /start-trial` (high) - Missing: ui_invocation
- `GET /license-info/{template_id}` (critical) - Missing: test, ui_invocation
- `GET /user-licenses/{user_id}` (critical) - Missing: test, ui_invocation

### src.api.llm_connector
**Gaps:** 6

- `initialize_llm_services` (high) - Missing: test, ui_invocation, cli_invocation
- `check_ollama_connection` (high) - Missing: test, ui_invocation, cli_invocation
- `install_model` (high) - Missing: test, ui_invocation, cli_invocation
- `get_model_info` (critical) - Missing: test, ui_invocation, cli_invocation
- `generate_response` (high) - Missing: test, ui_invocation, cli_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation

### src.api.local_llm_api
**Gaps:** 53

- `check_ollama_connection` (high) - Missing: test, ui_invocation, cli_invocation
- `update_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `select_model_for_task` (high) - Missing: test, ui_invocation, cli_invocation
- `health_check` (medium) - Missing: ui_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation
- `get_models` (critical) - Missing: test, ui_invocation, cli_invocation
- `pull_model` (high) - Missing: test, ui_invocation, cli_invocation
- `chat` (high) - Missing: ui_invocation, cli_invocation
- `get_profiles` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_profiles` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_model_recommendations` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_connection_pool_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_system_specs` (critical) - Missing: test, ui_invocation, cli_invocation
- `repair_websocket` (high) - Missing: test, ui_invocation, cli_invocation
- `get_offline_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `download_offline_model` (high) - Missing: test, ui_invocation, cli_invocation
- `generate_offline` (high) - Missing: test, ui_invocation, cli_invocation
- `get_cached_models` (critical) - Missing: test, ui_invocation, cli_invocation
- `activate_emergency_mode` (high) - Missing: test, ui_invocation, cli_invocation
- `get_circuit_breaker_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `reset_circuit_breaker` (high) - Missing: test, ui_invocation, cli_invocation
- `reset_all_circuit_breakers` (high) - Missing: test, ui_invocation, cli_invocation
- `save_settings` (high) - Missing: test, ui_invocation, cli_invocation
- `get_settings` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_claude_code_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_available_endpoint` (critical) - Missing: test, ui_invocation, cli_invocation
- `make_request` (high) - Missing: ui_invocation, cli_invocation
- `GET /api/health` (high) - Missing: ui_invocation
- `GET /api/status` (high) - Missing: ui_invocation
- `GET /api/models` (critical) - Missing: test, ui_invocation
- `POST /api/models/pull` (critical) - Missing: test, ui_invocation
- `POST /api/chat` (high) - Missing: ui_invocation
- `GET /api/profiles` (critical) - Missing: test, ui_invocation
- `PUT /api/profiles` (critical) - Missing: test, ui_invocation
- `POST /api/test` (high) - Missing: ui_invocation
- `GET /api/metrics` (high) - Missing: ui_invocation
- `GET /api/recommendations` (critical) - Missing: test, ui_invocation
- `GET /api/connection-pool` (critical) - Missing: test, ui_invocation
- `GET /api/system-specs` (critical) - Missing: test, ui_invocation
- `POST /api/websocket/repair` (critical) - Missing: test, ui_invocation
- `GET /api/offline/status` (critical) - Missing: test, ui_invocation
- `POST /api/offline/models/download` (critical) - Missing: test, ui_invocation
- `POST /api/offline/generate` (critical) - Missing: test, ui_invocation
- `GET /api/offline/models/cache` (critical) - Missing: test, ui_invocation
- `POST /api/offline/models/cleanup` (critical) - Missing: test, ui_invocation
- `POST /api/offline/emergency` (critical) - Missing: test, ui_invocation
- `GET /api/circuit-breakers/status` (critical) - Missing: test, ui_invocation
- `POST /api/circuit-breakers/<service_name>/reset` (critical) - Missing: test, ui_invocation
- `POST /api/circuit-breakers/reset-all` (critical) - Missing: test, ui_invocation
- `POST /api/settings` (critical) - Missing: test, ui_invocation
- `GET /api/settings` (critical) - Missing: test, ui_invocation
- `GET /api/claude-code/status` (critical) - Missing: test, ui_invocation

### src.api.metrics
**Gaps:** 17

- `get_current_user` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_system_health` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_system_health` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_spec2_compliance` (critical) - Missing: test, ui_invocation, cli_invocation
- `run_smoke_tests` (critical) - Missing: test, ui_invocation
- `run_load_tests` (critical) - Missing: test, ui_invocation
- `get_real_time_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_dashboard_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `GET /smoke-tests` (critical) - Missing: test, ui_invocation
- `GET /load-tests` (critical) - Missing: test, ui_invocation
- `GET /system-health` (critical) - Missing: test, ui_invocation
- `GET /spec2-compliance` (critical) - Missing: test, ui_invocation
- `GET /run-smoke-tests` (critical) - Missing: test, ui_invocation
- `GET /run-load-tests` (critical) - Missing: test, ui_invocation
- `GET /real-time` (critical) - Missing: test, ui_invocation
- `GET /dashboard-summary` (critical) - Missing: test, ui_invocation
- `GET /trigger-test-suite` (critical) - Missing: test, ui_invocation

### src.api.mimic_api
**Gaps:** 36

- `get_current_user` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_mimic_persona` (critical) - Missing: test, ui_invocation, cli_invocation
- `generate_persona` (high) - Missing: ui_invocation, cli_invocation
- `record_performance` (high) - Missing: ui_invocation, cli_invocation
- `get_performance_analytics` (critical) - Missing: ui_invocation, cli_invocation
- `fork_persona` (high) - Missing: ui_invocation, cli_invocation
- `merge_personas` (high) - Missing: ui_invocation, cli_invocation
- `add_plugin_extension` (high) - Missing: ui_invocation, cli_invocation
- `get_plugin_extensions` (critical) - Missing: test, ui_invocation, cli_invocation
- `add_knowledge` (high) - Missing: test, ui_invocation, cli_invocation
- `get_knowledge` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_persona_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_performance_tier` (critical) - Missing: ui_invocation, cli_invocation
- `export_persona_memory` (high) - Missing: test, ui_invocation, cli_invocation
- `import_persona_memory` (high) - Missing: test, ui_invocation, cli_invocation
- `list_personas` (high) - Missing: test, ui_invocation, cli_invocation
- `delete_persona` (critical) - Missing: test, ui_invocation, cli_invocation
- `health_check` (medium) - Missing: ui_invocation
- `mimic_error_handler` (high) - Missing: test, ui_invocation, cli_invocation
- `http_error_handler` (high) - Missing: test, ui_invocation, cli_invocation
- `GET /api/mimic/persona/generate` (high) - Missing: ui_invocation
- `GET /api/mimic/persona/{persona_id}/performance` (high) - Missing: ui_invocation
- `GET /api/mimic/persona/{persona_id}/analytics` (high) - Missing: ui_invocation
- `GET /api/mimic/persona/fork` (high) - Missing: ui_invocation
- `GET /api/mimic/persona/merge` (high) - Missing: ui_invocation
- `GET /api/mimic/persona/{persona_id}/plugin` (high) - Missing: ui_invocation
- `GET /api/mimic/persona/{persona_id}/plugins` (critical) - Missing: test, ui_invocation
- `GET /api/mimic/persona/{persona_id}/knowledge` (critical) - Missing: test, ui_invocation
- `GET /api/mimic/persona/{persona_id}/knowledge` (critical) - Missing: test, ui_invocation
- `GET /api/mimic/persona/{persona_id}/status` (critical) - Missing: test, ui_invocation
- `GET /api/mimic/persona/{persona_id}/tier` (high) - Missing: ui_invocation
- `GET /api/mimic/persona/{persona_id}/export` (critical) - Missing: test, ui_invocation
- `GET /api/mimic/persona/{persona_id}/import` (critical) - Missing: test, ui_invocation
- `GET /api/mimic/personas` (critical) - Missing: test, ui_invocation
- `GET /api/mimic/persona/{persona_id}` (critical) - Missing: test, ui_invocation
- `GET /api/mimic/health` (high) - Missing: ui_invocation

### src.api.offline_llm_manager
**Gaps:** 4

- `generate_response` (high) - Missing: test, ui_invocation, cli_invocation
- `get_system_status` (critical) - Missing: ui_invocation, cli_invocation
- `health_monitor` (high) - Missing: ui_invocation, cli_invocation
- `connection_monitor` (high) - Missing: test, ui_invocation, cli_invocation

### src.api.sentry_api
**Gaps:** 31

- `add_monitoring_event` (high) - Missing: test, ui_invocation, cli_invocation
- `add_alert` (high) - Missing: ui_invocation, cli_invocation
- `check_service_health` (high) - Missing: test, ui_invocation, cli_invocation
- `get_vault_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_claude_connector_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_synapse_gateway_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_launch_page_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_token_usage_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_system_metrics` (critical) - Missing: ui_invocation, cli_invocation
- `update_system_health` (critical) - Missing: test, ui_invocation, cli_invocation
- `monitoring_loop` (high) - Missing: test, ui_invocation, cli_invocation
- `start_monitoring` (high) - Missing: test, ui_invocation, cli_invocation
- `stop_monitoring_service` (high) - Missing: test, ui_invocation, cli_invocation
- `health_check` (medium) - Missing: ui_invocation
- `get_system_health` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_recent_events` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_active_alerts` (critical) - Missing: test, ui_invocation, cli_invocation
- `acknowledge_alert` (high) - Missing: test, ui_invocation, cli_invocation
- `resolve_alert` (high) - Missing: test, ui_invocation, cli_invocation
- `start_monitoring_endpoint` (critical) - Missing: test, ui_invocation, cli_invocation
- `stop_monitoring_endpoint` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_monitoring_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `GET /api/sentry/health` (high) - Missing: ui_invocation
- `GET /api/sentry/system-health` (critical) - Missing: test, ui_invocation
- `GET /api/sentry/events` (critical) - Missing: test, ui_invocation
- `GET /api/sentry/alerts` (critical) - Missing: test, ui_invocation
- `POST /api/sentry/alerts/<alert_id>/acknowledge` (critical) - Missing: test, ui_invocation
- `POST /api/sentry/alerts/<alert_id>/resolve` (critical) - Missing: test, ui_invocation
- `POST /api/sentry/start` (critical) - Missing: test, ui_invocation
- `POST /api/sentry/stop` (critical) - Missing: test, ui_invocation
- `GET /api/sentry/status` (critical) - Missing: test, ui_invocation

### src.api.settings_api
**Gaps:** 14

- `load_settings` (high) - Missing: test, ui_invocation, cli_invocation
- `save_settings` (high) - Missing: test, ui_invocation, cli_invocation
- `get_settings` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_settings` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_ollama_models` (critical) - Missing: test, ui_invocation, cli_invocation
- `health_check` (medium) - Missing: ui_invocation
- `GET /api/settings` (critical) - Missing: test, ui_invocation
- `POST /api/settings` (critical) - Missing: test, ui_invocation
- `POST /api/test/google-ai` (critical) - Missing: test, ui_invocation
- `POST /api/test/claude-code` (critical) - Missing: test, ui_invocation
- `POST /api/test/ollama` (critical) - Missing: test, ui_invocation
- `POST /api/test/local-llm` (critical) - Missing: test, ui_invocation
- `GET /api/models/ollama` (critical) - Missing: test, ui_invocation
- `GET /api/health` (high) - Missing: ui_invocation

### src.api.simple_backend
**Gaps:** 15

- `check_ollama_connection` (high) - Missing: test, ui_invocation, cli_invocation
- `generate_ollama_response` (high) - Missing: test, ui_invocation, cli_invocation
- `get_services` (critical) - Missing: test, ui_invocation, cli_invocation
- `delegate_task` (high) - Missing: test, ui_invocation, cli_invocation
- `get_stats` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_settings` (critical) - Missing: test, ui_invocation, cli_invocation
- `save_settings` (high) - Missing: test, ui_invocation, cli_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation
- `GET /api/project/services` (critical) - Missing: test, ui_invocation
- `POST /api/project/delegate` (critical) - Missing: test, ui_invocation
- `GET /api/project/stats` (critical) - Missing: test, ui_invocation
- `GET /api/settings` (critical) - Missing: test, ui_invocation
- `POST /api/settings` (critical) - Missing: test, ui_invocation
- `POST /api/test/<service>` (high) - Missing: ui_invocation
- `GET /api/status` (high) - Missing: ui_invocation

### src.api.superclaude_api
**Gaps:** 21

- `check_backend_availability` (high) - Missing: test, ui_invocation, cli_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation
- `create_session` (high) - Missing: ui_invocation
- `chat` (high) - Missing: ui_invocation, cli_invocation
- `list_sessions` (high) - Missing: test, ui_invocation, cli_invocation
- `delete_session` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_circuit_breakers_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `reset_circuit_breaker` (high) - Missing: test, ui_invocation, cli_invocation
- `add_message` (high) - Missing: test, ui_invocation, cli_invocation
- `get_context` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_token_usage` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_command` (critical) - Missing: test, ui_invocation, cli_invocation
- `enhance_prompt` (high) - Missing: test, ui_invocation, cli_invocation
- `execute_request` (critical) - Missing: test, ui_invocation, cli_invocation
- `GET /api/superclaude/status` (high) - Missing: ui_invocation
- `POST /api/superclaude/session` (high) - Missing: ui_invocation
- `POST /api/superclaude/chat` (high) - Missing: ui_invocation
- `GET /api/superclaude/sessions` (critical) - Missing: test, ui_invocation
- `DELETE /api/superclaude/session/<session_id>` (critical) - Missing: test, ui_invocation
- `GET /api/superclaude/circuit-breakers/status` (critical) - Missing: test, ui_invocation
- `POST /api/superclaude/circuit-breakers/<service_name>/reset` (critical) - Missing: test, ui_invocation

### src.api.synapse_connector
**Gaps:** 5

- `initialize_synapse` (high) - Missing: test, ui_invocation, cli_invocation
- `call_claude_api` (critical) - Missing: test, ui_invocation, cli_invocation
- `call_google_ai_api` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_connection_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_available_models` (critical) - Missing: test, ui_invocation, cli_invocation

### src.api.system_health
**Gaps:** 27

- `llm_health` (high) - Missing: test, ui_invocation, cli_invocation
- `vault_health` (high) - Missing: test, ui_invocation, cli_invocation
- `synapse_health` (high) - Missing: test, ui_invocation, cli_invocation
- `core_health` (high) - Missing: test, ui_invocation, cli_invocation
- `sentry_health` (high) - Missing: test, ui_invocation, cli_invocation
- `system_memory` (high) - Missing: test, ui_invocation, cli_invocation
- `system_health` (high) - Missing: test, ui_invocation, cli_invocation
- `get_memory_usage` (critical) - Missing: test, ui_invocation, cli_invocation
- `vault_stats` (high) - Missing: test, ui_invocation, cli_invocation
- `vault_memories` (high) - Missing: test, ui_invocation, cli_invocation
- `vault_audit_log` (high) - Missing: test, ui_invocation, cli_invocation
- `connect_llm` (high) - Missing: test, ui_invocation, cli_invocation
- `connect_vault` (high) - Missing: test, ui_invocation, cli_invocation
- `connect_synapse` (high) - Missing: test, ui_invocation, cli_invocation
- `GET /api/llm/health` (critical) - Missing: test, ui_invocation
- `GET /api/vault/health` (high) - Missing: ui_invocation
- `GET /api/synapse/health` (critical) - Missing: test, ui_invocation
- `GET /api/core/health` (critical) - Missing: test, ui_invocation
- `GET /api/sentry/health` (critical) - Missing: test, ui_invocation
- `GET /api/system/memory` (critical) - Missing: test, ui_invocation
- `GET /api/system/health` (critical) - Missing: test, ui_invocation
- `GET /api/vault/stats` (critical) - Missing: test, ui_invocation
- `GET /api/vault/memories` (critical) - Missing: test, ui_invocation
- `GET /api/vault/audit-log` (critical) - Missing: test, ui_invocation
- `POST /api/connect/llm` (critical) - Missing: test, ui_invocation
- `POST /api/connect/vault` (critical) - Missing: test, ui_invocation
- `POST /api/connect/synapse` (critical) - Missing: test, ui_invocation

### src.api.task_templates
**Gaps:** 15

- `get_current_user` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_templates` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_template` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_template` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_template` (critical) - Missing: test, ui_invocation, cli_invocation
- `delete_template` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_audit_entry` (high) - Missing: test, ui_invocation, cli_invocation
- `get_audit_trail` (critical) - Missing: test, ui_invocation, cli_invocation
- `GET /` (high) - Missing: ui_invocation
- `GET /{template_id}` (critical) - Missing: test, ui_invocation
- `GET /` (high) - Missing: ui_invocation
- `GET /{template_id}` (critical) - Missing: test, ui_invocation
- `GET /{template_id}` (critical) - Missing: test, ui_invocation
- `GET /audit` (high) - Missing: ui_invocation
- `GET /audit/{entity_id}` (critical) - Missing: test, ui_invocation

### src.api.vault_api
**Gaps:** 23

- `initialize_vault` (high) - Missing: test, ui_invocation, cli_invocation
- `health_check` (medium) - Missing: ui_invocation
- `get_vault_stats` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_memories` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_memory` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_memory` (critical) - Missing: ui_invocation, cli_invocation
- `update_memory` (critical) - Missing: test, ui_invocation, cli_invocation
- `delete_memory` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_audit_log` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_backup` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_integrity` (high) - Missing: test, ui_invocation, cli_invocation
- `search_memories` (high) - Missing: test, ui_invocation, cli_invocation
- `GET /api/vault/health` (high) - Missing: ui_invocation
- `GET /api/vault/stats` (critical) - Missing: test, ui_invocation
- `GET /api/vault/memories` (critical) - Missing: test, ui_invocation
- `POST /api/vault/memories` (critical) - Missing: test, ui_invocation
- `GET /api/vault/memories/<memory_id>` (high) - Missing: ui_invocation
- `PUT /api/vault/memories/<memory_id>` (critical) - Missing: test, ui_invocation
- `DELETE /api/vault/memories/<memory_id>` (critical) - Missing: test, ui_invocation
- `GET /api/vault/audit-log` (critical) - Missing: test, ui_invocation
- `POST /api/vault/backup` (critical) - Missing: test, ui_invocation
- `GET /api/vault/integrity` (critical) - Missing: test, ui_invocation
- `POST /api/vault/search` (critical) - Missing: test, ui_invocation

### src.api.vault_connector
**Gaps:** 19

- `initialize_vault` (high) - Missing: test, ui_invocation, cli_invocation
- `encrypt_data` (high) - Missing: test, ui_invocation, cli_invocation
- `decrypt_data` (high) - Missing: test, ui_invocation, cli_invocation
- `store_persona` (high) - Missing: test, ui_invocation, cli_invocation
- `get_persona` (critical) - Missing: ui_invocation, cli_invocation
- `store_memory` (medium) - Missing: ui_invocation
- `get_memories` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_system_event` (high) - Missing: test, ui_invocation, cli_invocation
- `get_system_logs` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation
- `get_stats` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_memory` (critical) - Missing: ui_invocation, cli_invocation
- `create_memory` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_memory` (critical) - Missing: test, ui_invocation, cli_invocation
- `delete_memory` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_audit_log` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_backup` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_integrity` (high) - Missing: test, ui_invocation, cli_invocation
- `search_memories` (high) - Missing: test, ui_invocation, cli_invocation

### src.api_server
**Gaps:** 11

- `main` (medium) - Missing: ui_invocation
- `init_database` (high) - Missing: test, ui_invocation, cli_invocation
- `run` (medium) - Missing: ui_invocation
- `health_check` (medium) - Missing: ui_invocation
- `create_agent` (critical) - Missing: ui_invocation, cli_invocation
- `list_agents` (high) - Missing: test, ui_invocation, cli_invocation
- `get_agent` (high) - Missing: ui_invocation
- `create_token` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_tokens` (high) - Missing: test, ui_invocation, cli_invocation
- `verify_token` (high) - Missing: test, ui_invocation, cli_invocation
- `execute_command` (critical) - Missing: test, ui_invocation, cli_invocation

### src.backend.alden_backend
**Gaps:** 23

- `load_config` (high) - Missing: test, ui_invocation
- `startup_event` (high) - Missing: ui_invocation, cli_invocation
- `shutdown_event` (high) - Missing: ui_invocation, cli_invocation
- `process_query` (high) - Missing: ui_invocation
- `health_check` (medium) - Missing: ui_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation
- `initialize` (medium) - Missing: ui_invocation
- `close` (medium) - Missing: ui_invocation
- `initialize` (medium) - Missing: ui_invocation
- `generate_embeddings` (high) - Missing: test, ui_invocation, cli_invocation
- `rag_query` (high) - Missing: test, ui_invocation, cli_invocation
- `retrieve_relevant_memories` (high) - Missing: test, ui_invocation, cli_invocation
- `build_context_text` (high) - Missing: test, ui_invocation, cli_invocation
- `generate_llm_response` (high) - Missing: test, ui_invocation, cli_invocation
- `store_memory_slice` (high) - Missing: test, ui_invocation, cli_invocation
- `store_in_knowledge_graph` (high) - Missing: test, ui_invocation, cli_invocation
- `extract_entities` (high) - Missing: test, ui_invocation, cli_invocation
- `initialize` (medium) - Missing: ui_invocation
- `process_query` (high) - Missing: ui_invocation
- `get_or_create_context` (critical) - Missing: test, ui_invocation, cli_invocation
- `GET /query` (high) - Missing: ui_invocation
- `GET /health` (high) - Missing: ui_invocation
- `GET /status` (high) - Missing: ui_invocation

### src.cli.alden_cli
**Gaps:** 3

- `create_alden_cli` (critical) - Missing: test, ui_invocation, cli_invocation
- `main` (medium) - Missing: ui_invocation
- `run` (medium) - Missing: ui_invocation

### src.components.EmbeddedGrafana
**Gaps:** 1

- `EmbeddedGrafana` (high) - Missing: test, ui_invocation, cli_invocation

### src.components.LaunchPage
**Gaps:** 1

- `LaunchPage` (high) - Missing: test, ui_invocation, cli_invocation

### src.components.SentryMonitor
**Gaps:** 1

- `SentryMonitor` (medium) - Missing: ui_invocation, cli_invocation

### src.components.StartupSettings
**Gaps:** 1

- `StartupSettings` (critical) - Missing: test, ui_invocation, cli_invocation

### src.components.SynapseGateway
**Gaps:** 2

- `exportApiConfiguration` (high) - Missing: test, ui_invocation, cli_invocation
- `exportApiKeysSecure` (high) - Missing: test, ui_invocation, cli_invocation

### src.components.TaskDashboard
**Gaps:** 1

- `TaskDashboard` (medium) - Missing: ui_invocation, cli_invocation

### src.components.TaskEditor
**Gaps:** 1

- `TaskEditor` (medium) - Missing: ui_invocation, cli_invocation

### src.components.ui.index
**Gaps:** 8

- `Card` (critical) - Missing: test, ui_invocation, cli_invocation
- `CardContent` (critical) - Missing: test, ui_invocation, cli_invocation
- `Button` (high) - Missing: ui_invocation, cli_invocation
- `Input` (high) - Missing: ui_invocation, cli_invocation
- `Badge` (critical) - Missing: test, ui_invocation, cli_invocation
- `Alert` (high) - Missing: ui_invocation, cli_invocation
- `AlertTitle` (critical) - Missing: test, ui_invocation, cli_invocation
- `AlertDescription` (critical) - Missing: test, ui_invocation, cli_invocation

### src.core.SpriteEngine
**Gaps:** 99

- `constructor` (high) - Missing: ui_invocation, cli_invocation
- `recordModelActivation` (critical) - Missing: test, ui_invocation, cli_invocation
- `recordModelDeactivation` (critical) - Missing: test, ui_invocation, cli_invocation
- `recordModelRequest` (critical) - Missing: test, ui_invocation, cli_invocation
- `recordThermalEvent` (critical) - Missing: test, ui_invocation, cli_invocation
- `updateMemoryUsage` (critical) - Missing: test, ui_invocation, cli_invocation
- `logSentryEvent` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `getPowerMetrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `getModelActivationSummary` (critical) - Missing: test, ui_invocation, cli_invocation
- `constructor` (high) - Missing: ui_invocation, cli_invocation
- `startThermalMonitoring` (critical) - Missing: test, ui_invocation, cli_invocation
- `startMemoryMonitoring` (critical) - Missing: test, ui_invocation, cli_invocation
- `checkThermalStatus` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `checkMemoryPressure` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `enforceMemoryBudget` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `triggerEmergencyThermalShutdown` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `enableThermalThrottling` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `enablePowerSaveMode` (critical) - Missing: test, ui_invocation, cli_invocation
- `disableThermalThrottling` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `getSystemTemperature` (critical) - Missing: test, ui_invocation, cli_invocation
- `getGPUTemperature` (critical) - Missing: test, ui_invocation, cli_invocation
- `getMemoryUsage` (critical) - Missing: test, ui_invocation, cli_invocation
- `canLoadModel` (critical) - Missing: test, ui_invocation, cli_invocation
- `addPowerEnforcementCallback` (critical) - Missing: test, ui_invocation, cli_invocation
- `updatePowerBudget` (critical) - Missing: test, ui_invocation, cli_invocation
- `getPowerStatus` (critical) - Missing: test, ui_invocation, cli_invocation
- `shutdown` (high) - Missing: ui_invocation, cli_invocation
- `constructor` (high) - Missing: ui_invocation, cli_invocation
- `initialize` (high) - Missing: ui_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `handleEmergencyShutdown` (critical) - Missing: test, ui_invocation, cli_invocation
- `handleMemoryPressure` (critical) - Missing: test, ui_invocation, cli_invocation
- `handleThermalThrottling` (critical) - Missing: test, ui_invocation, cli_invocation
- `loadConfiguration` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `initializeAlwaysLoadedSprites` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `initializeAuditLogging` (critical) - Missing: test, ui_invocation, cli_invocation
- `processConversationalRequest` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `processVoiceInput` (critical) - Missing: test, ui_invocation, cli_invocation
- `routeRequest` (critical) - Missing: test, ui_invocation, cli_invocation
- `validateSecurity` (critical) - Missing: test, ui_invocation, cli_invocation
- `executeRequest` (critical) - Missing: test, ui_invocation, cli_invocation
- `executeWithSprites` (critical) - Missing: test, ui_invocation, cli_invocation
- `executeWithHeavyLLM` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `callSprite` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `extractPersonaFromResponse` (critical) - Missing: test, ui_invocation, cli_invocation
- `extractEngineFromResponse` (critical) - Missing: test, ui_invocation, cli_invocation
- `checkForSensitiveContent` (critical) - Missing: test, ui_invocation, cli_invocation
- `loadSprite` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `loadHeavyLLM` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `prepareMemoryIsolation` (critical) - Missing: test, ui_invocation, cli_invocation
- `performHotSwap` (critical) - Missing: test, ui_invocation, cli_invocation
- `gracefulEngineUnload` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `performEngineLoad` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `verifyEngineHealth` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `callModelLoadAPI` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `callModelUnloadAPI` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `createSwapTimeout` (critical) - Missing: test, ui_invocation, cli_invocation
- `unloadAllHeavyLLM` (critical) - Missing: test, ui_invocation, cli_invocation
- `auditLog` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `logTaskExecution` (critical) - Missing: test, ui_invocation, cli_invocation
- `generateTaskId` (critical) - Missing: test, ui_invocation, cli_invocation
- `getSessionId` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `getActiveSprites` (critical) - Missing: test, ui_invocation, cli_invocation
- `getLoadedEngines` (critical) - Missing: test, ui_invocation, cli_invocation
- `getHotSwapStatus` (critical) - Missing: test, ui_invocation, cli_invocation
- `getLastSwapTime` (critical) - Missing: test, ui_invocation, cli_invocation
- `calculateAverageLoadTime` (critical) - Missing: test, ui_invocation, cli_invocation
- `updateConfiguration` (critical) - Missing: test, ui_invocation, cli_invocation
- `getConfiguration` (critical) - Missing: test, ui_invocation, cli_invocation
- `getPowerMetrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `getModelActivationSummary` (critical) - Missing: test, ui_invocation, cli_invocation
- `recordThermalEvent` (critical) - Missing: test, ui_invocation, cli_invocation
- `updateMemoryUsage` (critical) - Missing: test, ui_invocation, cli_invocation
- `getTelemetryReport` (critical) - Missing: test, ui_invocation, cli_invocation
- `getPowerStatus` (critical) - Missing: test, ui_invocation, cli_invocation
- `updatePowerBudget` (critical) - Missing: test, ui_invocation, cli_invocation
- `canLoadModel` (critical) - Missing: test, ui_invocation, cli_invocation
- `shutdown` (high) - Missing: ui_invocation, cli_invocation

### src.core.api
**Gaps:** 33

- `get_app` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_session` (critical) - Missing: ui_invocation
- `get_session` (critical) - Missing: ui_invocation
- `get_active_sessions` (critical) - Missing: ui_invocation, cli_invocation
- `add_participant` (critical) - Missing: ui_invocation, cli_invocation
- `remove_participant` (critical) - Missing: ui_invocation, cli_invocation
- `get_session_participants` (critical) - Missing: test, ui_invocation, cli_invocation
- `start_turn_taking` (critical) - Missing: ui_invocation, cli_invocation
- `advance_turn` (critical) - Missing: ui_invocation, cli_invocation
- `create_breakout` (critical) - Missing: ui_invocation, cli_invocation
- `end_breakout` (critical) - Missing: ui_invocation, cli_invocation
- `share_insight` (critical) - Missing: ui_invocation, cli_invocation
- `export_session_log` (critical) - Missing: ui_invocation, cli_invocation
- `update_live_feed_settings` (critical) - Missing: test, ui_invocation, cli_invocation
- `pause_session` (critical) - Missing: ui_invocation, cli_invocation
- `resume_session` (critical) - Missing: ui_invocation, cli_invocation
- `end_session` (critical) - Missing: ui_invocation, cli_invocation
- `GET /api/core/session` (critical) - Missing: ui_invocation
- `GET /api/core/session/{session_id}` (critical) - Missing: ui_invocation
- `GET /api/core/sessions` (critical) - Missing: ui_invocation
- `GET /api/core/session/{session_id}/participants` (critical) - Missing: ui_invocation
- `GET /api/core/session/{session_id}/participants/{participant_id}` (critical) - Missing: ui_invocation
- `GET /api/core/session/{session_id}/participants` (critical) - Missing: test, ui_invocation
- `GET /api/core/session/{session_id}/turn-taking/start` (critical) - Missing: ui_invocation
- `GET /api/core/session/{session_id}/turn-taking/advance` (critical) - Missing: ui_invocation
- `GET /api/core/session/{session_id}/breakout` (critical) - Missing: ui_invocation
- `GET /api/core/session/{session_id}/breakout/{breakout_id}` (critical) - Missing: ui_invocation
- `GET /api/core/session/{session_id}/insights` (critical) - Missing: ui_invocation
- `GET /api/core/session/{session_id}/log` (critical) - Missing: ui_invocation
- `GET /api/core/session/{session_id}/settings` (critical) - Missing: test, ui_invocation
- `GET /api/core/session/{session_id}/pause` (critical) - Missing: ui_invocation
- `GET /api/core/session/{session_id}/resume` (critical) - Missing: ui_invocation
- `GET /api/core/session/{session_id}` (critical) - Missing: ui_invocation

### src.core.core
**Gaps:** 24

- `register_event_callback` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_session` (critical) - Missing: ui_invocation
- `add_participant` (critical) - Missing: ui_invocation, cli_invocation
- `remove_participant` (critical) - Missing: ui_invocation, cli_invocation
- `start_turn_taking` (critical) - Missing: ui_invocation, cli_invocation
- `advance_turn` (critical) - Missing: ui_invocation, cli_invocation
- `set_current_turn` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_breakout` (critical) - Missing: ui_invocation, cli_invocation
- `end_breakout` (critical) - Missing: ui_invocation, cli_invocation
- `share_insight` (critical) - Missing: ui_invocation, cli_invocation
- `get_session` (critical) - Missing: ui_invocation
- `get_active_sessions` (critical) - Missing: ui_invocation, cli_invocation
- `pause_session` (critical) - Missing: ui_invocation, cli_invocation
- `resume_session` (critical) - Missing: ui_invocation, cli_invocation
- `end_session` (critical) - Missing: ui_invocation, cli_invocation
- `export_session_log` (critical) - Missing: ui_invocation, cli_invocation
- `get_session_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `record_metric` (critical) - Missing: test, ui_invocation, cli_invocation
- `start_operation_timer` (critical) - Missing: test, ui_invocation, cli_invocation
- `end_operation_timer` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_performance_summary` (critical) - Missing: ui_invocation, cli_invocation
- `export_performance_data` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_performance_trends` (critical) - Missing: test, ui_invocation, cli_invocation
- `process_query_with_rag` (critical) - Missing: ui_invocation

### src.core.enhanced_core
**Gaps:** 6

- `create_agentic_session` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_agentic_task` (critical) - Missing: test, ui_invocation, cli_invocation
- `delegate_to_optimal_agent` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_agent_capabilities_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_workflow_status_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_enhanced_session_info` (critical) - Missing: test, ui_invocation, cli_invocation

### src.core.enhanced_session_manager
**Gaps:** 6

- `create_core_session` (critical) - Missing: test, ui_invocation, cli_invocation
- `add_participant` (critical) - Missing: ui_invocation, cli_invocation
- `sync_agent_memory_to_communal` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_breakout_room` (critical) - Missing: test, ui_invocation, cli_invocation
- `manage_turn_taking` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_session_performance_metrics` (critical) - Missing: test, ui_invocation, cli_invocation

### src.core.error_handling
**Gaps:** 18

- `register_error_callback` (critical) - Missing: test, ui_invocation, cli_invocation
- `register_recovery_strategy` (critical) - Missing: ui_invocation, cli_invocation
- `handle_error` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_error_summary` (critical) - Missing: ui_invocation, cli_invocation
- `reset_error_counts` (critical) - Missing: test, ui_invocation, cli_invocation
- `session_management_recovery` (critical) - Missing: ui_invocation, cli_invocation
- `participant_management_recovery` (critical) - Missing: ui_invocation, cli_invocation
- `turn_taking_recovery` (critical) - Missing: ui_invocation, cli_invocation
- `vault_integration_recovery` (critical) - Missing: ui_invocation, cli_invocation
- `system_recovery` (critical) - Missing: test, ui_invocation, cli_invocation
- `validate_session_id` (critical) - Missing: ui_invocation, cli_invocation
- `validate_participant_data` (critical) - Missing: ui_invocation, cli_invocation
- `validate_turn_order` (critical) - Missing: test, ui_invocation, cli_invocation
- `validate_breakout_participants` (critical) - Missing: test, ui_invocation, cli_invocation
- `record_error` (critical) - Missing: test, ui_invocation, cli_invocation
- `record_performance` (critical) - Missing: ui_invocation, cli_invocation
- `get_error_rate` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_performance_summary` (critical) - Missing: ui_invocation, cli_invocation

### src.core.kimi_k2_orchestration
**Gaps:** 9

- `create_agentic_workflow` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_agentic_workflow` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_agent_capabilities` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_workflow_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_active_workflows` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_workflow_stats` (critical) - Missing: test, ui_invocation, cli_invocation
- `pause_workflow` (critical) - Missing: test, ui_invocation, cli_invocation
- `resume_workflow` (critical) - Missing: test, ui_invocation, cli_invocation
- `cancel_workflow` (critical) - Missing: test, ui_invocation, cli_invocation

### src.core.logging_manager
**Gaps:** 12

- `create_core_logging_manager` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_session_event` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_participant_event` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_performance_metric` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_audit_event` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_error` (critical) - Missing: ui_invocation, cli_invocation
- `add_monitoring_callback` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_session_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_performance_summary` (critical) - Missing: ui_invocation, cli_invocation
- `get_audit_summary` (critical) - Missing: ui_invocation, cli_invocation
- `export_logs` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_log_statistics` (critical) - Missing: test, ui_invocation, cli_invocation

### src.core.mimic_integration
**Gaps:** 12

- `create_mimic_integration` (critical) - Missing: test, ui_invocation, cli_invocation
- `register_mimic_persona` (critical) - Missing: ui_invocation, cli_invocation
- `unregister_mimic_persona` (critical) - Missing: test, ui_invocation, cli_invocation
- `recommend_personas_for_session` (critical) - Missing: ui_invocation, cli_invocation
- `add_persona_to_session` (critical) - Missing: ui_invocation, cli_invocation
- `remove_persona_from_session` (critical) - Missing: ui_invocation, cli_invocation
- `share_insight_in_session` (critical) - Missing: ui_invocation, cli_invocation
- `record_session_performance` (critical) - Missing: ui_invocation, cli_invocation
- `get_session_insights` (critical) - Missing: ui_invocation, cli_invocation
- `get_session_performance_summary` (critical) - Missing: ui_invocation, cli_invocation
- `get_active_sessions` (critical) - Missing: ui_invocation, cli_invocation
- `get_integration_status` (critical) - Missing: ui_invocation, cli_invocation

### src.core.session_manager
**Gaps:** 21

- `get_session_manager` (critical) - Missing: ui_invocation
- `demo_session_management` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_session` (critical) - Missing: ui_invocation
- `get_session` (critical) - Missing: ui_invocation
- `update_session_activity` (critical) - Missing: test, ui_invocation, cli_invocation
- `add_conversation_message` (critical) - Missing: ui_invocation
- `get_conversation_history` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_recent_context` (critical) - Missing: test, ui_invocation, cli_invocation
- `extend_session` (critical) - Missing: test, ui_invocation, cli_invocation
- `terminate_session` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_user_sessions` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_session_stats` (critical) - Missing: test, ui_invocation, cli_invocation
- `request_turn` (critical) - Missing: test, ui_invocation, cli_invocation
- `release_turn` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_current_turn` (critical) - Missing: test, ui_invocation, cli_invocation
- `propagate_context` (critical) - Missing: test, ui_invocation, cli_invocation
- `start_conversation` (critical) - Missing: test, ui_invocation, cli_invocation
- `send_user_message` (critical) - Missing: test, ui_invocation, cli_invocation
- `send_agent_response` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_conversation_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `main` (critical) - Missing: ui_invocation

### src.database.alden_memory_manager
**Gaps:** 11

- `create_alden_memory_manager` (critical) - Missing: test, ui_invocation, cli_invocation
- `initialize` (critical) - Missing: ui_invocation
- `generate_memory_id` (critical) - Missing: test, ui_invocation, cli_invocation
- `generate_session_id` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_session` (critical) - Missing: ui_invocation
- `store_memory` (critical) - Missing: ui_invocation
- `semantic_search` (critical) - Missing: ui_invocation, cli_invocation
- `hybrid_search` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_session_memories` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_memory_statistics` (critical) - Missing: test, ui_invocation, cli_invocation
- `health_check` (critical) - Missing: ui_invocation

### src.database.backup_manager
**Gaps:** 5

- `main` (critical) - Missing: ui_invocation
- `create_backup` (critical) - Missing: test, ui_invocation, cli_invocation
- `restore_backup` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_backups` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_backup_status` (critical) - Missing: test, ui_invocation, cli_invocation

### src.database.database_manager
**Gaps:** 31

- `get_database_manager` (critical) - Missing: ui_invocation
- `initialize_database` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_schema_version_1` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_connection` (critical) - Missing: test, ui_invocation, cli_invocation
- `initialize_schema` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_schema_version` (critical) - Missing: ui_invocation
- `transaction` (critical) - Missing: ui_invocation, cli_invocation
- `create_user` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_user` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_user_by_username` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_user_preferences` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_username` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_agent` (critical) - Missing: ui_invocation, cli_invocation
- `get_agent` (critical) - Missing: ui_invocation
- `get_user_agents` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_agent_activity` (critical) - Missing: test, ui_invocation, cli_invocation
- `store_memory` (critical) - Missing: ui_invocation
- `search_memories` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_memory_stats` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_session` (critical) - Missing: ui_invocation
- `get_session` (critical) - Missing: ui_invocation
- `update_session_activity` (critical) - Missing: test, ui_invocation, cli_invocation
- `store_conversation` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_conversation_history` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_personality_trait` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_personality_profile` (critical) - Missing: test, ui_invocation, cli_invocation
- `record_metric` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `vacuum_database` (critical) - Missing: test, ui_invocation, cli_invocation
- `backup_database` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_database_stats` (critical) - Missing: test, ui_invocation, cli_invocation

### src.database.long_term_memory_manager
**Gaps:** 15

- `create_long_term_memory_manager` (critical) - Missing: test, ui_invocation, cli_invocation
- `archive_memories_by_policy` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_manual_archive` (critical) - Missing: test, ui_invocation, cli_invocation
- `retrieve_from_archive` (critical) - Missing: test, ui_invocation, cli_invocation
- `optimize_session_cache` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_session_cache` (critical) - Missing: test, ui_invocation, cli_invocation
- `consolidate_similar_memories` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_consolidation_clusters` (critical) - Missing: test, ui_invocation, cli_invocation
- `build_memory_hierarchy` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_memory_hierarchy` (critical) - Missing: test, ui_invocation, cli_invocation
- `analyze_session_patterns` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_session_patterns` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_long_term_utilization` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_optimization_insights` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_long_term_statistics` (critical) - Missing: test, ui_invocation, cli_invocation

### src.database.migration_v1_1
**Gaps:** 3

- `apply_migration_v11` (critical) - Missing: test, ui_invocation, cli_invocation
- `apply_migration` (critical) - Missing: test, ui_invocation, cli_invocation
- `rollback_migration` (critical) - Missing: test, ui_invocation, cli_invocation

### src.database.pgvector_client
**Gaps:** 8

- `connect` (critical) - Missing: ui_invocation
- `disconnect` (critical) - Missing: test, ui_invocation, cli_invocation
- `store_memory_slice` (critical) - Missing: test, ui_invocation, cli_invocation
- `semantic_search` (critical) - Missing: ui_invocation, cli_invocation
- `hybrid_search` (critical) - Missing: test, ui_invocation, cli_invocation
- `store_reasoning_chain` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_memory_statistics` (critical) - Missing: test, ui_invocation, cli_invocation
- `health_check` (critical) - Missing: ui_invocation

### src.embedding.semantic_embedding_service
**Gaps:** 10

- `generate_embedding` (high) - Missing: ui_invocation, cli_invocation
- `generate_embeddings_batch` (high) - Missing: test, ui_invocation, cli_invocation
- `embed_memory_slice` (high) - Missing: test, ui_invocation, cli_invocation
- `get_statistics` (critical) - Missing: test, ui_invocation, cli_invocation
- `clear_cache` (high) - Missing: test, ui_invocation, cli_invocation
- `initialize` (medium) - Missing: ui_invocation
- `store_memory_with_embedding` (high) - Missing: test, ui_invocation, cli_invocation
- `semantic_retrieve` (high) - Missing: test, ui_invocation, cli_invocation
- `hybrid_retrieve` (high) - Missing: test, ui_invocation, cli_invocation
- `get_comprehensive_statistics` (critical) - Missing: test, ui_invocation, cli_invocation

### src.hooks.useClaudeConnector
**Gaps:** 9

- `useClaudeConnector` (high) - Missing: test, ui_invocation, cli_invocation
- `useClaudeChat` (high) - Missing: test, ui_invocation, cli_invocation
- `useClaudeChat` (high) - Missing: test, ui_invocation, cli_invocation
- `useClaudeCodeGen` (high) - Missing: test, ui_invocation, cli_invocation
- `useClaudeCodeGen` (high) - Missing: test, ui_invocation, cli_invocation
- `useClaudeAnalysis` (high) - Missing: test, ui_invocation, cli_invocation
- `useClaudeAnalysis` (high) - Missing: test, ui_invocation, cli_invocation
- `useClaudeDocumentProcessor` (high) - Missing: test, ui_invocation, cli_invocation
- `useClaudeDocumentProcessor` (high) - Missing: test, ui_invocation, cli_invocation

### src.hooks.useKimiK2
**Gaps:** 5

- `useKimiK2Chat` (high) - Missing: test, ui_invocation, cli_invocation
- `useKimiK2CodeGen` (high) - Missing: test, ui_invocation, cli_invocation
- `useKimiK2Agentic` (high) - Missing: test, ui_invocation, cli_invocation
- `useKimiK2LongContext` (high) - Missing: test, ui_invocation, cli_invocation
- `useKimiK2Analysis` (high) - Missing: test, ui_invocation, cli_invocation

### src.hooks.useTauriIntegration
**Gaps:** 4

- `useTauriIntegration` (high) - Missing: test, ui_invocation, cli_invocation
- `isTauriApp` (high) - Missing: test, ui_invocation, cli_invocation
- `useTauriFileSystem` (high) - Missing: test, ui_invocation, cli_invocation
- `useTauriFileSystem` (high) - Missing: test, ui_invocation, cli_invocation

### src.llm.ClaudeConnector
**Gaps:** 2

- `createClaudeConnector` (high) - Missing: test, ui_invocation, cli_invocation
- `getClaudeConnector` (high) - Missing: test, ui_invocation, cli_invocation

### src.llm.llm_selection_layer
**Gaps:** 11

- `create_llm_selection_layer` (critical) - Missing: test, ui_invocation, cli_invocation
- `select_optimal_model` (high) - Missing: test, ui_invocation, cli_invocation
- `switch_model` (high) - Missing: test, ui_invocation, cli_invocation
- `get_current_model_info` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_available_models` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_model_performance_stats` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_swap_history` (critical) - Missing: test, ui_invocation, cli_invocation
- `generate_with_current_model` (high) - Missing: test, ui_invocation, cli_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation
- `shutdown` (high) - Missing: ui_invocation, cli_invocation
- `health_check_worker` (high) - Missing: test, ui_invocation, cli_invocation

### src.llm.local_llm_client
**Gaps:** 10

- `create_llm_client` (critical) - Missing: test, ui_invocation, cli_invocation
- `call` (medium) - Missing: ui_invocation
- `get_connection` (critical) - Missing: test, ui_invocation, cli_invocation
- `record_error` (high) - Missing: test, ui_invocation, cli_invocation
- `record_success` (high) - Missing: test, ui_invocation, cli_invocation
- `health_check` (medium) - Missing: ui_invocation
- `get_pool_stats` (critical) - Missing: test, ui_invocation, cli_invocation
- `generate` (medium) - Missing: ui_invocation
- `list_models` (high) - Missing: test, ui_invocation, cli_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation

### src.log_handling.agent_token_tracker
**Gaps:** 12

- `get_token_tracker` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_agent_token_usage` (high) - Missing: test, ui_invocation, cli_invocation
- `get_agent_performance_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_compliance_report` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_token_usage` (high) - Missing: test, ui_invocation, cli_invocation
- `get_agent_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_usage_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_claude_integration_compliance_report` (critical) - Missing: test, ui_invocation, cli_invocation
- `export_logs` (high) - Missing: test, ui_invocation, cli_invocation
- `get_log_file_path` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_system_status` (critical) - Missing: ui_invocation, cli_invocation

### src.log_handling.exception_handler
**Gaps:** 9

- `log_exception` (high) - Missing: test, ui_invocation, cli_invocation
- `log_error` (high) - Missing: ui_invocation, cli_invocation
- `get_instance` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_exception` (high) - Missing: test, ui_invocation, cli_invocation
- `log_error` (high) - Missing: ui_invocation, cli_invocation
- `get_log_file_path` (critical) - Missing: test, ui_invocation, cli_invocation
- `set_log_level` (high) - Missing: test, ui_invocation, cli_invocation
- `export_logs` (high) - Missing: test, ui_invocation, cli_invocation
- `clear_logs` (high) - Missing: test, ui_invocation, cli_invocation

### src.main
**Gaps:** 12

- `main` (medium) - Missing: ui_invocation
- `format` (medium) - Missing: ui_invocation
- `log_startup` (high) - Missing: ui_invocation, cli_invocation
- `log_shutdown` (high) - Missing: ui_invocation, cli_invocation
- `log_error` (high) - Missing: ui_invocation, cli_invocation
- `log_critical_error` (high) - Missing: ui_invocation, cli_invocation
- `start` (medium) - Missing: ui_invocation
- `stop` (medium) - Missing: ui_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation
- `simulate_error` (high) - Missing: ui_invocation, cli_invocation
- `start` (medium) - Missing: ui_invocation
- `signal_handler` (high) - Missing: test, ui_invocation, cli_invocation

### src.memory.memory_pruning_manager
**Gaps:** 4

- `main` (medium) - Missing: ui_invocation
- `analyze_conversations` (high) - Missing: test, ui_invocation, cli_invocation
- `prune_conversations` (high) - Missing: test, ui_invocation, cli_invocation
- `get_memory_usage_stats` (critical) - Missing: test, ui_invocation, cli_invocation

### src.personas.alden
**Gaps:** 13

- `create_alden_persona` (critical) - Missing: test, ui_invocation, cli_invocation
- `generate_response` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_trait` (critical) - Missing: test, ui_invocation, cli_invocation
- `add_correction_event` (critical) - Missing: test, ui_invocation, cli_invocation
- `record_session_mood` (critical) - Missing: test, ui_invocation, cli_invocation
- `export_memory` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation
- `optimize_self` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_ecosystem_health` (critical) - Missing: test, ui_invocation, cli_invocation
- `store_conversation_memory` (critical) - Missing: test, ui_invocation, cli_invocation
- `retrieve_similar_memories` (critical) - Missing: test, ui_invocation, cli_invocation
- `generate_reasoning_chain` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_enhanced_memory_statistics` (critical) - Missing: test, ui_invocation, cli_invocation

### src.personas.alden.AldenInterface
**Gaps:** 8

- `AldenInterface` (critical) - Missing: test, ui_invocation, cli_invocation
- `delegateToGoogle` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `handleSendMessage` (critical) - Missing: test, ui_invocation, cli_invocation
- `generateResponse` (critical) - Missing: test, ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `getRadialPosition` (critical) - Missing: test, ui_invocation, cli_invocation
- `renderScreen` (critical) - Missing: test, ui_invocation, cli_invocation

### src.personas.alden_semantic_adapter
**Gaps:** 7

- `create_alden_semantic_adapter` (critical) - Missing: test, ui_invocation, cli_invocation
- `initialize_semantic_manager` (critical) - Missing: test, ui_invocation, cli_invocation
- `generate_enhanced_response` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_semantic_statistics` (critical) - Missing: test, ui_invocation, cli_invocation
- `health_check` (critical) - Missing: ui_invocation
- `generate` (critical) - Missing: ui_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation

### src.personas.mimic
**Gaps:** 11

- `create_mimic_persona` (critical) - Missing: test, ui_invocation, cli_invocation
- `generate_persona` (high) - Missing: ui_invocation, cli_invocation
- `record_performance` (high) - Missing: ui_invocation, cli_invocation
- `fork_persona` (high) - Missing: ui_invocation, cli_invocation
- `merge_personas` (high) - Missing: ui_invocation, cli_invocation
- `add_plugin_extension` (high) - Missing: ui_invocation, cli_invocation
- `get_performance_analytics` (critical) - Missing: ui_invocation, cli_invocation
- `get_performance_tier` (critical) - Missing: ui_invocation, cli_invocation
- `export_memory` (high) - Missing: test, ui_invocation, cli_invocation
- `import_memory` (high) - Missing: test, ui_invocation, cli_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation

### src.personas.sentry.sentry
**Gaps:** 9

- `constructor` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `catch` (high) - Missing: ui_invocation, cli_invocation
- `getSentryPersona` (critical) - Missing: test, ui_invocation, cli_invocation

### src.run_alden
**Gaps:** 5

- `load_config` (high) - Missing: test, ui_invocation
- `get_llm_config` (critical) - Missing: test, ui_invocation, cli_invocation
- `run_cli` (critical) - Missing: test, ui_invocation, cli_invocation
- `run_api` (critical) - Missing: test, ui_invocation, cli_invocation
- `main` (medium) - Missing: ui_invocation

### src.run_services
**Gaps:** 3

- `main` (medium) - Missing: ui_invocation
- `start_services` (high) - Missing: test, ui_invocation, cli_invocation
- `signal_handler` (high) - Missing: test, ui_invocation, cli_invocation

### src.services.memory_sync_service
**Gaps:** 13

- `create_memory_sync_service` (critical) - Missing: test, ui_invocation, cli_invocation
- `initialize` (medium) - Missing: ui_invocation
- `acquire_memory_lock` (high) - Missing: test, ui_invocation, cli_invocation
- `release_memory_lock` (high) - Missing: test, ui_invocation, cli_invocation
- `sync_agent_memories` (high) - Missing: test, ui_invocation, cli_invocation
- `resolve_conflict` (high) - Missing: test, ui_invocation, cli_invocation
- `get_agent_memory_slice` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_sync_statistics` (critical) - Missing: test, ui_invocation, cli_invocation
- `health_check` (medium) - Missing: ui_invocation
- `sync_worker` (high) - Missing: test, ui_invocation, cli_invocation
- `health_check` (medium) - Missing: ui_invocation
- `get_session_memories` (critical) - Missing: test, ui_invocation, cli_invocation
- `semantic_search` (high) - Missing: ui_invocation, cli_invocation

### src.services.multi_agent_memory_coordinator
**Gaps:** 8

- `create_multi_agent_coordinator` (critical) - Missing: test, ui_invocation, cli_invocation
- `initialize` (medium) - Missing: ui_invocation
- `register_agent` (high) - Missing: test, ui_invocation, cli_invocation
- `store_agent_memory` (high) - Missing: test, ui_invocation, cli_invocation
- `search_agent_memories` (high) - Missing: test, ui_invocation, cli_invocation
- `sync_all_agents` (high) - Missing: test, ui_invocation, cli_invocation
- `get_memory_allocation` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_coordinator_status` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.agent_handoff
**Gaps:** 10

- `get_handoff_manager` (critical) - Missing: ui_invocation
- `demo_agent_handoff` (critical) - Missing: test, ui_invocation, cli_invocation
- `initiate_handoff` (critical) - Missing: ui_invocation
- `hydrate_target_agent_context` (critical) - Missing: ui_invocation
- `get_handoff_status` (critical) - Missing: ui_invocation
- `cancel_handoff` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_agent_capabilities` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_active_handoffs` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_handoff_history` (critical) - Missing: test, ui_invocation, cli_invocation
- `main` (critical) - Missing: ui_invocation

### src.synapse.api
**Gaps:** 69

- `get_synapse` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_handoff_manager` (critical) - Missing: ui_invocation
- `get_current_user` (critical) - Missing: test, ui_invocation, cli_invocation
- `initialize_synapse` (critical) - Missing: test, ui_invocation, cli_invocation
- `register_plugin` (critical) - Missing: ui_invocation, cli_invocation
- `approve_plugin` (critical) - Missing: ui_invocation, cli_invocation
- `revoke_plugin` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_plugin` (critical) - Missing: ui_invocation, cli_invocation
- `get_plugin_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_plugins` (critical) - Missing: test, ui_invocation, cli_invocation
- `request_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `approve_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `deny_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_pending_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `request_connection` (critical) - Missing: ui_invocation, cli_invocation
- `approve_connection` (critical) - Missing: ui_invocation, cli_invocation
- `close_connection` (critical) - Missing: ui_invocation, cli_invocation
- `get_connections` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_webhooks` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_webhook` (critical) - Missing: test, ui_invocation, cli_invocation
- `run_benchmark` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_benchmark_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_traffic_logs` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_traffic_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `export_traffic_logs` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_system_status` (critical) - Missing: ui_invocation, cli_invocation
- `export_system_data` (critical) - Missing: test, ui_invocation, cli_invocation
- `save_settings` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_settings` (critical) - Missing: test, ui_invocation, cli_invocation
- `health_check` (critical) - Missing: ui_invocation
- `initiate_handoff` (critical) - Missing: ui_invocation
- `get_handoff_status` (critical) - Missing: ui_invocation
- `cancel_handoff` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_active_handoffs` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_handoff_history` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_agent_capabilities` (critical) - Missing: test, ui_invocation, cli_invocation
- `GET /api/synapse/plugin/register` (critical) - Missing: ui_invocation
- `GET /api/synapse/plugin/{plugin_id}/approve` (critical) - Missing: ui_invocation
- `GET /api/synapse/plugin/{plugin_id}/revoke` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/plugin/{plugin_id}/execute` (critical) - Missing: ui_invocation
- `GET /api/synapse/plugin/{plugin_id}/status` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/plugins` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/plugin/{plugin_id}/permissions/request` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/permissions/{request_id}/approve` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/permissions/{request_id}/deny` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/permissions/pending` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/connection/request` (critical) - Missing: ui_invocation
- `GET /api/synapse/connection/{connection_id}/approve` (critical) - Missing: ui_invocation
- `GET /api/synapse/connection/{connection_id}/close` (critical) - Missing: ui_invocation
- `GET /api/synapse/connections` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/webhooks` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/webhooks` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/plugin/{plugin_id}/benchmark` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/plugin/{plugin_id}/benchmark` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/traffic/logs` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/traffic/summary` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/traffic/export` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/system/status` (critical) - Missing: ui_invocation
- `GET /api/synapse/system/export` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/system/cleanup` (critical) - Missing: ui_invocation
- `GET /api/settings` (critical) - Missing: test, ui_invocation
- `GET /api/settings` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/health` (critical) - Missing: ui_invocation
- `GET /api/synapse/handoff/{source_agent_id}/initiate` (critical) - Missing: ui_invocation
- `GET /api/synapse/handoff/{handoff_id}/status` (critical) - Missing: ui_invocation
- `GET /api/synapse/handoff/{handoff_id}/cancel` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/handoffs/active` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/handoffs/history` (critical) - Missing: test, ui_invocation
- `GET /api/synapse/agents/capabilities` (critical) - Missing: test, ui_invocation

### src.synapse.api.mcp_endpoints
**Gaps:** 25

- `get_mcp_manager` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_mcp_servers` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_mcp_server` (critical) - Missing: test, ui_invocation, cli_invocation
- `start_mcp_server` (critical) - Missing: test, ui_invocation, cli_invocation
- `stop_mcp_server` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_mcp_server_tools` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_mcp_tool` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_mcp_server_health` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_all_mcp_health` (critical) - Missing: test, ui_invocation, cli_invocation
- `send_gmail` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_gmail_emails` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_calendar_events` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_calendar_event` (critical) - Missing: test, ui_invocation, cli_invocation
- `GET /servers` (critical) - Missing: ui_invocation
- `GET /servers/{server_id}` (critical) - Missing: test, ui_invocation
- `GET /servers/{server_id}/start` (critical) - Missing: test, ui_invocation
- `GET /servers/{server_id}/stop` (critical) - Missing: test, ui_invocation
- `GET /servers/{server_id}/tools` (critical) - Missing: test, ui_invocation
- `GET /servers/{server_id}/execute` (critical) - Missing: test, ui_invocation
- `GET /servers/{server_id}/health` (critical) - Missing: test, ui_invocation
- `GET /health` (critical) - Missing: ui_invocation
- `GET /gmail/send` (critical) - Missing: test, ui_invocation
- `GET /gmail/emails` (critical) - Missing: test, ui_invocation
- `GET /calendar/events` (critical) - Missing: test, ui_invocation
- `GET /calendar/events` (critical) - Missing: test, ui_invocation

### src.synapse.audit_logger
**Gaps:** 15

- `get_audit_logger` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_outbound_request` (critical) - Missing: ui_invocation, cli_invocation
- `log_agent_interaction` (critical) - Missing: ui_invocation, cli_invocation
- `log_permission_check` (critical) - Missing: ui_invocation, cli_invocation
- `log_security_violation` (critical) - Missing: ui_invocation, cli_invocation
- `log_event` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_outbound_request` (critical) - Missing: ui_invocation, cli_invocation
- `log_agent_interaction` (critical) - Missing: ui_invocation, cli_invocation
- `log_permission_check` (critical) - Missing: ui_invocation, cli_invocation
- `log_rate_limit` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_security_violation` (critical) - Missing: ui_invocation, cli_invocation
- `log_browser_preview` (critical) - Missing: ui_invocation, cli_invocation
- `log_webhook_config` (critical) - Missing: ui_invocation, cli_invocation
- `get_audit_summary` (critical) - Missing: ui_invocation, cli_invocation
- `verify_log_integrity` (critical) - Missing: ui_invocation, cli_invocation

### src.synapse.benchmark
**Gaps:** 9

- `start_benchmark` (critical) - Missing: test, ui_invocation, cli_invocation
- `complete_benchmark` (critical) - Missing: test, ui_invocation, cli_invocation
- `run_benchmark` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_benchmark_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_recent_benchmarks` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_performance_tier` (critical) - Missing: ui_invocation, cli_invocation
- `get_risk_score` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_benchmarked_plugins` (critical) - Missing: test, ui_invocation, cli_invocation
- `export_benchmark_data` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.browser_preview
**Gaps:** 10

- `create_browser_session` (critical) - Missing: ui_invocation, cli_invocation
- `preview_url` (critical) - Missing: ui_invocation, cli_invocation
- `get_session_info` (critical) - Missing: ui_invocation, cli_invocation
- `get_policy` (critical) - Missing: ui_invocation, cli_invocation
- `validate_url` (critical) - Missing: ui_invocation, cli_invocation
- `sanitize_html` (critical) - Missing: ui_invocation, cli_invocation
- `create_session` (critical) - Missing: ui_invocation
- `preview_url` (critical) - Missing: ui_invocation, cli_invocation
- `get_session_info` (critical) - Missing: ui_invocation, cli_invocation
- `block_domain` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.browser_preview_integration
**Gaps:** 28

- `create_agent_browser_session` (critical) - Missing: ui_invocation, cli_invocation
- `preview_url_for_agent` (critical) - Missing: ui_invocation, cli_invocation
- `start_live_preview_for_agent` (critical) - Missing: test, ui_invocation, cli_invocation
- `stop_live_preview` (critical) - Missing: ui_invocation, cli_invocation
- `get_agent_session_info` (critical) - Missing: ui_invocation, cli_invocation
- `get_whitelist_status` (critical) - Missing: ui_invocation, cli_invocation
- `add_allowed_domain` (critical) - Missing: ui_invocation, cli_invocation
- `remove_allowed_domain` (critical) - Missing: ui_invocation, cli_invocation
- `is_url_allowed` (critical) - Missing: ui_invocation, cli_invocation
- `add_allowed_domain` (critical) - Missing: ui_invocation, cli_invocation
- `remove_allowed_domain` (critical) - Missing: ui_invocation, cli_invocation
- `add_blocked_domain` (critical) - Missing: ui_invocation, cli_invocation
- `remove_blocked_domain` (critical) - Missing: test, ui_invocation, cli_invocation
- `start_live_preview` (critical) - Missing: ui_invocation, cli_invocation
- `stop_live_preview` (critical) - Missing: ui_invocation, cli_invocation
- `get_active_previews` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_agent_session` (critical) - Missing: ui_invocation, cli_invocation
- `preview_url_for_agent` (critical) - Missing: ui_invocation, cli_invocation
- `start_live_preview_for_agent` (critical) - Missing: test, ui_invocation, cli_invocation
- `stop_live_preview` (critical) - Missing: ui_invocation, cli_invocation
- `get_agent_session_info` (critical) - Missing: ui_invocation, cli_invocation
- `get_all_session_info` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_whitelist_status` (critical) - Missing: ui_invocation, cli_invocation
- `add_allowed_domain` (critical) - Missing: ui_invocation, cli_invocation
- `remove_allowed_domain` (critical) - Missing: ui_invocation, cli_invocation
- `add_blocked_domain` (critical) - Missing: ui_invocation, cli_invocation
- `remove_blocked_domain` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_live_previews` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.browser_preview_ui
**Gaps:** 2

- `create_browser_preview_ui` (critical) - Missing: test, ui_invocation, cli_invocation
- `destroy` (critical) - Missing: ui_invocation, cli_invocation

### src.synapse.claude_gateway
**Gaps:** 13

- `create_claude_gateway` (critical) - Missing: test, ui_invocation, cli_invocation
- `prompt_must_not_be_empty` (critical) - Missing: test, ui_invocation, cli_invocation
- `agent_id_must_be_valid` (critical) - Missing: test, ui_invocation, cli_invocation
- `run` (critical) - Missing: ui_invocation
- `security_middleware` (critical) - Missing: test, ui_invocation, cli_invocation
- `health_check` (critical) - Missing: ui_invocation
- `validate_claude_request` (critical) - Missing: test, ui_invocation, cli_invocation
- `append_to_vault` (critical) - Missing: test, ui_invocation, cli_invocation
- `process_claude_directive` (critical) - Missing: test, ui_invocation, cli_invocation
- `GET /api/health` (critical) - Missing: ui_invocation
- `GET /api/claude/validate` (critical) - Missing: test, ui_invocation
- `GET /api/vault/append` (critical) - Missing: test, ui_invocation
- `GET /directives` (critical) - Missing: test, ui_invocation

### src.synapse.config
**Gaps:** 8

- `to_dict` (critical) - Missing: test, ui_invocation, cli_invocation
- `from_dict` (critical) - Missing: test, ui_invocation, cli_invocation
- `load_config` (critical) - Missing: test, ui_invocation
- `save_config` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_default_config` (critical) - Missing: test, ui_invocation, cli_invocation
- `validate_config` (critical) - Missing: ui_invocation
- `get_environment_config` (critical) - Missing: test, ui_invocation, cli_invocation
- `merge_configs` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.credential_manager
**Gaps:** 25

- `add_credential` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_credential` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_credential_password` (critical) - Missing: test, ui_invocation, cli_invocation
- `search_credentials` (critical) - Missing: test, ui_invocation, cli_invocation
- `request_injection` (critical) - Missing: test, ui_invocation, cli_invocation
- `approve_injection` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_injection` (critical) - Missing: test, ui_invocation, cli_invocation
- `encrypt` (critical) - Missing: ui_invocation
- `decrypt` (critical) - Missing: ui_invocation
- `get_master_key` (critical) - Missing: test, ui_invocation, cli_invocation
- `add_credential` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_credential` (critical) - Missing: test, ui_invocation, cli_invocation
- `delete_credential` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_credential` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_credential_password` (critical) - Missing: test, ui_invocation, cli_invocation
- `search_credentials` (critical) - Missing: test, ui_invocation, cli_invocation
- `request_injection` (critical) - Missing: test, ui_invocation, cli_invocation
- `approve_injection` (critical) - Missing: test, ui_invocation, cli_invocation
- `deny_injection` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_injection` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_pending_injections` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_injection_history` (critical) - Missing: test, ui_invocation, cli_invocation
- `add_domain_mapping` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_related_domains` (critical) - Missing: test, ui_invocation, cli_invocation
- `validate_credential` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.manifest
**Gaps:** 7

- `to_dict` (critical) - Missing: test, ui_invocation, cli_invocation
- `to_json` (critical) - Missing: test, ui_invocation, cli_invocation
- `calculate_signature` (critical) - Missing: test, ui_invocation, cli_invocation
- `validate_signature` (critical) - Missing: test, ui_invocation, cli_invocation
- `validate_manifest` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_manifest` (critical) - Missing: test, ui_invocation, cli_invocation
- `load_manifest_from_json` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.mcp_executor
**Gaps:** 3

- `execute_filesystem_mcp` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_github_mcp` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_gmail_calendar_mcp` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.mcp_plugin_manager
**Gaps:** 17

- `initialize_mcp_plugin_manager` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_mcp_plugin_manager` (critical) - Missing: test, ui_invocation, cli_invocation
- `initialize` (critical) - Missing: ui_invocation
- `load_server_registry` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_default_registry` (critical) - Missing: test, ui_invocation, cli_invocation
- `discover_mcp_plugins` (critical) - Missing: test, ui_invocation, cli_invocation
- `register_plugin_from_manifest` (critical) - Missing: test, ui_invocation, cli_invocation
- `validate_mcp_manifest` (critical) - Missing: test, ui_invocation, cli_invocation
- `auto_start_servers` (critical) - Missing: test, ui_invocation, cli_invocation
- `start_mcp_server` (critical) - Missing: test, ui_invocation, cli_invocation
- `stop_mcp_server` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_mcp_tool` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_server_info` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_active_servers` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_available_tools` (critical) - Missing: test, ui_invocation, cli_invocation
- `health_check_all_servers` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_server_registry` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.permissions
**Gaps:** 10

- `request_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `approve_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `deny_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `revoke_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_permission` (critical) - Missing: ui_invocation, cli_invocation
- `get_plugin_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_pending_requests` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_plugin_grants` (critical) - Missing: test, ui_invocation, cli_invocation
- `export_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `import_permissions` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.plugin_manager
**Gaps:** 13

- `register_plugin` (critical) - Missing: ui_invocation, cli_invocation
- `approve_plugin` (critical) - Missing: ui_invocation, cli_invocation
- `revoke_plugin` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_plugin` (critical) - Missing: ui_invocation, cli_invocation
- `get_plugin_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_plugins` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_plugin_manifest` (critical) - Missing: test, ui_invocation, cli_invocation
- `export_plugin_data` (critical) - Missing: test, ui_invocation, cli_invocation
- `add_plugin` (critical) - Missing: ui_invocation, cli_invocation
- `remove_plugin` (critical) - Missing: test, ui_invocation, cli_invocation
- `activate_plugin` (critical) - Missing: test, ui_invocation, cli_invocation
- `deactivate_plugin` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_plugins` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.plugins.google-ai.plugin
**Gaps:** 2

- `create_agent` (critical) - Missing: ui_invocation, cli_invocation
- `execute` (critical) - Missing: ui_invocation

### src.synapse.sandbox
**Gaps:** 5

- `create_sandbox` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_in_sandbox` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_sandbox_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_active_sandboxes` (critical) - Missing: test, ui_invocation, cli_invocation
- `monitor_resources` (critical) - Missing: ui_invocation, cli_invocation

### src.synapse.security_manager
**Gaps:** 11

- `check_synapse_permission` (critical) - Missing: ui_invocation, cli_invocation
- `get_security_summary` (critical) - Missing: ui_invocation, cli_invocation
- `get_agent_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_security_event` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_rate_limit` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_rate_limit_status` (critical) - Missing: ui_invocation, cli_invocation
- `check_permission` (critical) - Missing: ui_invocation, cli_invocation
- `get_security_summary` (critical) - Missing: ui_invocation, cli_invocation
- `get_agent_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_rate_limit_status_for_agent` (critical) - Missing: ui_invocation, cli_invocation
- `clear_security_events` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.security_monitor
**Gaps:** 22

- `register_default_hooks` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_webhook_request` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_api_call` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_browser_preview` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_credential_access` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_credential_injection` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_security_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_rate_limit` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_rate_limit_status` (critical) - Missing: ui_invocation, cli_invocation
- `check_permission` (critical) - Missing: ui_invocation, cli_invocation
- `request_approval` (critical) - Missing: test, ui_invocation, cli_invocation
- `approve_request` (critical) - Missing: test, ui_invocation, cli_invocation
- `deny_request` (critical) - Missing: test, ui_invocation, cli_invocation
- `register_security_hook` (critical) - Missing: test, ui_invocation, cli_invocation
- `log_security_event` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_and_log_request` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_security_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `stop` (critical) - Missing: ui_invocation
- `webhook_security_hook` (critical) - Missing: test, ui_invocation, cli_invocation
- `credential_security_hook` (critical) - Missing: test, ui_invocation, cli_invocation
- `rate_limit_hook` (critical) - Missing: test, ui_invocation, cli_invocation
- `permission_hook` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.security_ui
**Gaps:** 3

- `create_security_dashboard` (critical) - Missing: test, ui_invocation, cli_invocation
- `show` (critical) - Missing: ui_invocation
- `show` (critical) - Missing: ui_invocation

### src.synapse.sentry_integration
**Gaps:** 19

- `monitor_synapse_operation` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_sentry_monitor` (critical) - Missing: test, ui_invocation, cli_invocation
- `register_module_for_monitoring` (critical) - Missing: test, ui_invocation, cli_invocation
- `monitor_outbound_request` (critical) - Missing: ui_invocation, cli_invocation
- `monitor_agent_interaction` (critical) - Missing: ui_invocation, cli_invocation
- `monitor_browser_preview` (critical) - Missing: ui_invocation, cli_invocation
- `monitor_webhook_config` (critical) - Missing: ui_invocation, cli_invocation
- `monitor_credential_access` (critical) - Missing: ui_invocation, cli_invocation
- `register_module` (critical) - Missing: ui_invocation, cli_invocation
- `add_alert_callback` (critical) - Missing: ui_invocation, cli_invocation
- `monitor_outbound_request` (critical) - Missing: ui_invocation, cli_invocation
- `monitor_agent_interaction` (critical) - Missing: ui_invocation, cli_invocation
- `monitor_browser_preview` (critical) - Missing: ui_invocation, cli_invocation
- `monitor_webhook_config` (critical) - Missing: ui_invocation, cli_invocation
- `monitor_credential_access` (critical) - Missing: ui_invocation, cli_invocation
- `get_monitoring_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `decorator` (critical) - Missing: test, ui_invocation
- `async_wrapper` (critical) - Missing: test, ui_invocation, cli_invocation
- `sync_wrapper` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.sentry_siem
**Gaps:** 26

- `register_agent_process` (critical) - Missing: test, ui_invocation, cli_invocation
- `assess_process_risk` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_process_report` (critical) - Missing: test, ui_invocation, cli_invocation
- `analyze_connection` (critical) - Missing: test, ui_invocation, cli_invocation
- `detect_anomaly` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_baseline` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_network_report` (critical) - Missing: test, ui_invocation, cli_invocation
- `establish_baseline` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_behavioral_anomaly` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_behavioral_report` (critical) - Missing: test, ui_invocation, cli_invocation
- `respond_to_threat` (critical) - Missing: test, ui_invocation, cli_invocation
- `is_agent_quarantined` (critical) - Missing: ui_invocation, cli_invocation
- `release_quarantine` (critical) - Missing: test, ui_invocation, cli_invocation
- `monitor_agent_transaction` (critical) - Missing: ui_invocation, cli_invocation
- `get_security_report` (critical) - Missing: ui_invocation, cli_invocation
- `register_agent_process` (critical) - Missing: test, ui_invocation, cli_invocation
- `is_agent_quarantined` (critical) - Missing: ui_invocation, cli_invocation
- `release_quarantine` (critical) - Missing: test, ui_invocation, cli_invocation
- `shutdown` (critical) - Missing: ui_invocation, cli_invocation
- `name` (critical) - Missing: ui_invocation
- `cmdline` (critical) - Missing: test, ui_invocation, cli_invocation
- `cpu_percent` (critical) - Missing: test, ui_invocation, cli_invocation
- `memory_percent` (critical) - Missing: test, ui_invocation, cli_invocation
- `connections` (critical) - Missing: ui_invocation, cli_invocation
- `create_time` (critical) - Missing: test, ui_invocation, cli_invocation
- `ppid` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.synapse
**Gaps:** 37

- `register_plugin` (critical) - Missing: ui_invocation, cli_invocation
- `approve_plugin` (critical) - Missing: ui_invocation, cli_invocation
- `revoke_plugin` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_plugin` (critical) - Missing: ui_invocation, cli_invocation
- `get_plugin_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_plugins` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_plugin_manifest` (critical) - Missing: test, ui_invocation, cli_invocation
- `request_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `approve_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `deny_permissions` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_permission` (critical) - Missing: ui_invocation, cli_invocation
- `get_pending_permission_requests` (critical) - Missing: test, ui_invocation, cli_invocation
- `request_connection` (critical) - Missing: ui_invocation, cli_invocation
- `approve_connection` (critical) - Missing: ui_invocation, cli_invocation
- `close_connection` (critical) - Missing: ui_invocation, cli_invocation
- `run_benchmark` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_benchmark_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_performance_tier` (critical) - Missing: ui_invocation, cli_invocation
- `get_risk_score` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_traffic_logs` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_traffic_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `export_traffic_logs` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_traffic_statistics` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_sandbox_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_active_sandboxes` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_system_status` (critical) - Missing: ui_invocation, cli_invocation
- `export_system_data` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_traffic_metrics` (critical) - Missing: ui_invocation, cli_invocation
- `get_security_report` (critical) - Missing: ui_invocation, cli_invocation
- `update_user_bandwidth` (critical) - Missing: ui_invocation, cli_invocation
- `register_agent_process` (critical) - Missing: test, ui_invocation, cli_invocation
- `is_agent_quarantined` (critical) - Missing: ui_invocation, cli_invocation
- `release_agent_quarantine` (critical) - Missing: test, ui_invocation, cli_invocation
- `launch_local_resource` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_connections` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_webhooks` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_webhook` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.traffic_logger
**Gaps:** 6

- `log_traffic` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_traffic_logs` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_traffic_summary` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_connection_logs` (critical) - Missing: test, ui_invocation, cli_invocation
- `export_traffic_logs` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_traffic_statistics` (critical) - Missing: test, ui_invocation, cli_invocation

### src.synapse.traffic_manager
**Gaps:** 13

- `consume` (critical) - Missing: test, ui_invocation, cli_invocation
- `update` (critical) - Missing: ui_invocation
- `get_user_budget` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_user_budget` (critical) - Missing: test, ui_invocation, cli_invocation
- `record_request` (critical) - Missing: test, ui_invocation, cli_invocation
- `detect_anomaly` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_security_report` (critical) - Missing: ui_invocation, cli_invocation
- `get_agent_priority` (critical) - Missing: test, ui_invocation, cli_invocation
- `submit_request` (critical) - Missing: ui_invocation, cli_invocation
- `get_system_metrics` (critical) - Missing: ui_invocation, cli_invocation
- `get_security_report` (critical) - Missing: ui_invocation, cli_invocation
- `update_user_budget` (critical) - Missing: test, ui_invocation, cli_invocation
- `shutdown` (critical) - Missing: ui_invocation, cli_invocation

### src.synapse.webhook_manager
**Gaps:** 13

- `create_webhook` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_webhook` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_webhooks` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_webhook` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_webhook` (critical) - Missing: test, ui_invocation, cli_invocation
- `update_webhook` (critical) - Missing: test, ui_invocation, cli_invocation
- `delete_webhook` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_webhook` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_webhooks` (critical) - Missing: test, ui_invocation, cli_invocation
- `execute_webhook` (critical) - Missing: test, ui_invocation, cli_invocation
- `validate_webhook_config` (critical) - Missing: test, ui_invocation, cli_invocation
- `list_webhooks_cli` (critical) - Missing: test, ui_invocation, cli_invocation
- `create_webhook_cli` (critical) - Missing: test, ui_invocation, cli_invocation

### src.utils.APIManager
**Gaps:** 9

- `call` (medium) - Missing: ui_invocation
- `callExternal` (high) - Missing: test, ui_invocation, cli_invocation
- `sendToModule` (high) - Missing: test, ui_invocation, cli_invocation
- `emit` (high) - Missing: test, ui_invocation, cli_invocation
- `on` (medium) - Missing: ui_invocation
- `off` (medium) - Missing: ui_invocation
- `getServices` (high) - Missing: test, ui_invocation, cli_invocation
- `getEndpoints` (high) - Missing: test, ui_invocation, cli_invocation
- `getAPIStats` (high) - Missing: test, ui_invocation, cli_invocation

### src.utils.AuthenticationManager
**Gaps:** 9

- `authenticate` (high) - Missing: test, ui_invocation, cli_invocation
- `logout` (high) - Missing: test, ui_invocation, cli_invocation
- `hasPermission` (high) - Missing: test, ui_invocation, cli_invocation
- `checkPermission` (high) - Missing: test, ui_invocation, cli_invocation
- `isAuthenticated` (high) - Missing: test, ui_invocation, cli_invocation
- `getCurrentUser` (high) - Missing: test, ui_invocation, cli_invocation
- `getAuthState` (high) - Missing: test, ui_invocation, cli_invocation
- `validateSession` (high) - Missing: test, ui_invocation, cli_invocation
- `getAuthStats` (high) - Missing: test, ui_invocation, cli_invocation

### src.utils.ConfigManager
**Gaps:** 10

- `exportConfiguration` (high) - Missing: test, ui_invocation, cli_invocation
- `get` (medium) - Missing: ui_invocation
- `set` (medium) - Missing: ui_invocation
- `watch` (high) - Missing: test, ui_invocation
- `getEnvironment` (high) - Missing: test, ui_invocation, cli_invocation
- `isProduction` (high) - Missing: test, ui_invocation, cli_invocation
- `isDevelopment` (high) - Missing: test, ui_invocation, cli_invocation
- `exportConfig` (high) - Missing: test, ui_invocation, cli_invocation
- `importConfig` (high) - Missing: test, ui_invocation, cli_invocation
- `getConfigStats` (high) - Missing: test, ui_invocation, cli_invocation

### src.utils.DelegationMetrics
**Gaps:** 1

- `exportMetrics` (high) - Missing: test, ui_invocation, cli_invocation

### src.utils.ErrorHandler
**Gaps:** 5

- `exportErrorHistory` (high) - Missing: test, ui_invocation, cli_invocation
- `handleError` (high) - Missing: test, ui_invocation, cli_invocation
- `getErrorHistory` (high) - Missing: test, ui_invocation, cli_invocation
- `getErrorStats` (high) - Missing: test, ui_invocation, cli_invocation
- `exportErrorHistory` (high) - Missing: test, ui_invocation, cli_invocation

### src.utils.HealthMonitor
**Gaps:** 7

- `getSystemHealth` (high) - Missing: test, ui_invocation, cli_invocation
- `getModuleHealth` (high) - Missing: test, ui_invocation, cli_invocation
- `recordMetric` (high) - Missing: test, ui_invocation, cli_invocation
- `createAlert` (high) - Missing: test, ui_invocation, cli_invocation
- `getDiagnosticReport` (high) - Missing: test, ui_invocation, cli_invocation
- `getHealthStats` (high) - Missing: test, ui_invocation, cli_invocation
- `acknowledgeAlert` (high) - Missing: test, ui_invocation, cli_invocation

### src.utils.SystemLogger
**Gaps:** 15

- `exportLogs` (high) - Missing: test, ui_invocation, cli_invocation
- `debug` (high) - Missing: ui_invocation, cli_invocation
- `info` (medium) - Missing: ui_invocation
- `warn` (medium) - Missing: ui_invocation
- `error` (medium) - Missing: ui_invocation
- `userAction` (high) - Missing: test, ui_invocation, cli_invocation
- `apiCall` (high) - Missing: ui_invocation, cli_invocation
- `agentAction` (high) - Missing: test, ui_invocation, cli_invocation
- `securityEvent` (high) - Missing: test, ui_invocation, cli_invocation
- `performance` (medium) - Missing: ui_invocation
- `createContext` (high) - Missing: test, ui_invocation, cli_invocation
- `withContext` (high) - Missing: test, ui_invocation, cli_invocation
- `getLogs` (high) - Missing: test, ui_invocation, cli_invocation
- `exportLogs` (high) - Missing: test, ui_invocation, cli_invocation
- `getLogStats` (high) - Missing: test, ui_invocation, cli_invocation

### src.utils.automatic_recovery_orchestrator
**Gaps:** 16

- `start_automatic_recovery` (high) - Missing: test, ui_invocation, cli_invocation
- `stop_automatic_recovery` (high) - Missing: test, ui_invocation, cli_invocation
- `get_recovery_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `force_service_recovery` (high) - Missing: test, ui_invocation, cli_invocation
- `register_event_callback` (high) - Missing: test, ui_invocation, cli_invocation
- `assess_system_health` (high) - Missing: test, ui_invocation, cli_invocation
- `detect_service_failures` (high) - Missing: test, ui_invocation, cli_invocation
- `queue_recovery` (high) - Missing: test, ui_invocation, cli_invocation
- `execute_recovery` (critical) - Missing: test, ui_invocation, cli_invocation
- `recovery_worker` (high) - Missing: test, ui_invocation, cli_invocation
- `monitoring_loop` (high) - Missing: test, ui_invocation, cli_invocation
- `start_orchestrator` (high) - Missing: test, ui_invocation, cli_invocation
- `stop_orchestrator` (high) - Missing: test, ui_invocation, cli_invocation
- `get_orchestrator_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `generate_status_report` (high) - Missing: test, ui_invocation, cli_invocation
- `signal_handler` (high) - Missing: test, ui_invocation, cli_invocation

### src.utils.circuit_breaker
**Gaps:** 17

- `with_circuit_breaker` (high) - Missing: test, ui_invocation, cli_invocation
- `record_success` (high) - Missing: test, ui_invocation, cli_invocation
- `record_failure` (high) - Missing: test, ui_invocation, cli_invocation
- `record_state_change` (high) - Missing: test, ui_invocation, cli_invocation
- `get_failure_rate` (critical) - Missing: test, ui_invocation, cli_invocation
- `to_dict` (high) - Missing: test, ui_invocation, cli_invocation
- `call` (medium) - Missing: ui_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation
- `reset` (high) - Missing: ui_invocation, cli_invocation
- `get_or_create` (critical) - Missing: ui_invocation, cli_invocation
- `get_breaker` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_all_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `reset_all` (high) - Missing: ui_invocation, cli_invocation
- `remove_breaker` (high) - Missing: test, ui_invocation, cli_invocation
- `decorator` (high) - Missing: test, ui_invocation
- `unreliable_service` (high) - Missing: test, ui_invocation, cli_invocation
- `wrapper` (high) - Missing: test, ui_invocation, cli_invocation

### src.utils.env_loader
**Gaps:** 16

- `get_env` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_env_int` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_env_bool` (critical) - Missing: test, ui_invocation, cli_invocation
- `validate_environment` (high) - Missing: test, ui_invocation, cli_invocation
- `load_environment` (high) - Missing: test, ui_invocation, cli_invocation
- `get` (medium) - Missing: ui_invocation
- `get_int` (critical) - Missing: ui_invocation, cli_invocation
- `get_bool` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_float` (critical) - Missing: test, ui_invocation, cli_invocation
- `get_list` (critical) - Missing: test, ui_invocation, cli_invocation
- `validate_required_vars` (high) - Missing: test, ui_invocation
- `get_database_config` (critical) - Missing: test, ui_invocation
- `get_api_keys` (critical) - Missing: test, ui_invocation
- `get_security_config` (critical) - Missing: test, ui_invocation
- `get_service_config` (critical) - Missing: test, ui_invocation
- `print_summary` (medium) - Missing: ui_invocation

### src.utils.memory_optimizer
**Gaps:** 8

- `optimize_memory_storage` (high) - Missing: test, ui_invocation, cli_invocation
- `consolidate_alden_memory` (high) - Missing: test, ui_invocation, cli_invocation
- `create_optimized_schema` (critical) - Missing: test, ui_invocation, cli_invocation
- `merge_memory_file` (high) - Missing: test, ui_invocation, cli_invocation
- `insert_consolidated_record` (high) - Missing: test, ui_invocation, cli_invocation
- `optimize_vault_storage` (high) - Missing: test, ui_invocation, cli_invocation
- `archive_old_sessions` (high) - Missing: test, ui_invocation, cli_invocation
- `main` (medium) - Missing: ui_invocation

### src.utils.performance_optimizer
**Gaps:** 8

- `main` (medium) - Missing: ui_invocation
- `generate_cache_key` (high) - Missing: test, ui_invocation, cli_invocation
- `get_cached_response` (critical) - Missing: test, ui_invocation, cli_invocation
- `cache_response` (high) - Missing: test, ui_invocation, cli_invocation
- `optimize_prompt` (high) - Missing: test, ui_invocation, cli_invocation
- `optimize_llm_request` (high) - Missing: test, ui_invocation, cli_invocation
- `get_performance_metrics` (critical) - Missing: test, ui_invocation, cli_invocation
- `make_request` (high) - Missing: ui_invocation, cli_invocation

### src.utils.service_recovery_manager
**Gaps:** 14

- `start_service_recovery` (high) - Missing: test, ui_invocation, cli_invocation
- `stop_service_recovery` (high) - Missing: test, ui_invocation, cli_invocation
- `get_recovery_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `check_service_health` (high) - Missing: test, ui_invocation, cli_invocation
- `restart_service` (high) - Missing: test, ui_invocation, cli_invocation
- `heal_service` (high) - Missing: test, ui_invocation, cli_invocation
- `execute_recovery_action` (critical) - Missing: test, ui_invocation, cli_invocation
- `failover_service` (high) - Missing: test, ui_invocation, cli_invocation
- `emergency_stop_service` (high) - Missing: test, ui_invocation, cli_invocation
- `monitor_services` (high) - Missing: test, ui_invocation, cli_invocation
- `start_monitoring` (high) - Missing: test, ui_invocation, cli_invocation
- `stop_monitoring` (high) - Missing: test, ui_invocation, cli_invocation
- `get_service_status` (critical) - Missing: test, ui_invocation, cli_invocation
- `generate_recovery_report` (high) - Missing: test, ui_invocation, cli_invocation

### src.utils.service_watchdog
**Gaps:** 15

- `create_watchdog_service` (critical) - Missing: test, ui_invocation, cli_invocation
- `is_port_in_use` (high) - Missing: test, ui_invocation, cli_invocation
- `start_service` (high) - Missing: test, ui_invocation, cli_invocation
- `stop_service` (high) - Missing: test, ui_invocation, cli_invocation
- `restart_service` (high) - Missing: test, ui_invocation, cli_invocation
- `check_service_health` (high) - Missing: test, ui_invocation, cli_invocation
- `monitor_services` (high) - Missing: test, ui_invocation, cli_invocation
- `handle_service_failure` (critical) - Missing: test, ui_invocation, cli_invocation
- `start_all_services` (high) - Missing: test, ui_invocation, cli_invocation
- `stop_all_services` (high) - Missing: test, ui_invocation, cli_invocation
- `get_status` (critical) - Missing: ui_invocation, cli_invocation
- `start` (medium) - Missing: ui_invocation
- `stop` (medium) - Missing: ui_invocation
- `signal_handler` (high) - Missing: test, ui_invocation, cli_invocation
- `run_daemon` (critical) - Missing: test, ui_invocation, cli_invocation

## Quick Action Items

### Immediate (Critical + High Priority)

1. **Add missing tests:**
   - Add test for `create_token` in `src/api_server.py`
   - Add test for `execute_command` in `src/api_server.py`
   - Add test for `get_llm_config` in `src/run_alden.py`
   - Add test for `run_cli` in `src/run_alden.py`
   - Add test for `run_api` in `src/run_alden.py`
   - Add test for `create_alden_api` in `src/api/alden_api.py`
   - Add test for `update_trait` in `src/api/alden_api.py`
   - Add test for `get_version` in `src/api/claude_code_cli.py`
   - Add test for `execute_command` in `src/api/claude_code_cli.py`
   - Add test for `get_session_history` in `src/api/claude_code_cli.py`

2. **Add UI invocation paths:**
   - Add UI control for `create_agent`
   - Add UI control for `create_token`
   - Add UI control for `execute_command`
   - Add UI control for `get_status`
   - Add UI control for `get_llm_config`
   - Add UI control for `run_cli`
   - Add UI control for `run_api`
   - Add UI control for `create_alden_api`
   - Add UI control for `update_trait`
   - Add UI control for `get_status`

3. **Add CLI invocation paths:**
   - Add CLI command for `create_agent`
   - Add CLI command for `create_token`
   - Add CLI command for `execute_command`
   - Add CLI command for `get_status`
   - Add CLI command for `get_llm_config`
   - Add CLI command for `run_cli`
   - Add CLI command for `run_api`
   - Add CLI command for `create_alden_api`
   - Add CLI command for `update_trait`
   - Add CLI command for `get_status`

---
*Generated by SPEC-3 Week 2 Coverage Gap Analyzer*