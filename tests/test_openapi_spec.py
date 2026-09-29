from pathlib import Path

from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename

SPEC_PATH = Path(__file__).parent.parent / 'docs' / 'openapi.yaml'


def load_spec():
    content, _ = read_from_filename(str(SPEC_PATH))
    return content


def test_openapi_spec_file_exists():
    assert SPEC_PATH.exists(), f'Файл спецификации не найден: {SPEC_PATH}'


def test_openapi_spec_is_valid_yaml():
    spec = load_spec()
    assert isinstance(spec, dict), 'Спецификация должна быть YAML-объектом'


def test_openapi_spec_has_required_fields():
    spec = load_spec()
    assert 'openapi' in spec, 'Отсутствует поле openapi'
    assert 'info' in spec, 'Отсутствует поле info'
    assert 'paths' in spec, 'Отсутствует поле paths'


def test_openapi_spec_validates():
    spec = load_spec()
    validate(spec)


def test_working_hours_boundary_excludes_18():
    spec = load_spec()
    validation_desc = str(spec['components']['responses']['ValidationError']['description'])
    assert '18:00' in validation_desc
    assert 'исключено' in validation_desc or 'exclusive' in validation_desc.lower()


def test_past_time_check_only_on_create():
    spec = load_spec()
    post_desc = str(spec['paths']['/api/bookings']['post']['description'])
    put_desc = str(spec['paths']['/api/bookings/{id}']['put']['description'])
    assert 'прошедш' in post_desc.lower() or 'создани' in post_desc.lower()
    assert 'прошедш' in put_desc.lower() or 'разрешен' in put_desc.lower()


def test_time_pattern_guarantees_30_min_grid():
    spec = load_spec()
    time_pattern = spec['components']['schemas']['CreateBookingRequest']['properties']['time']['pattern']
    assert '[03]0' in time_pattern or '00|30' in time_pattern


def test_client_name_has_min_length():
    spec = load_spec()
    client_name = spec['components']['schemas']['CreateBookingRequest']['properties']['client_name']
    assert client_name.get('minLength', 0) >= 1


def test_topic_has_min_length():
    spec = load_spec()
    topic = spec['components']['schemas']['CreateBookingRequest']['properties']['topic']
    assert topic.get('minLength', 0) >= 1


def test_recording_url_auto_generation_documented():
    spec = load_spec()
    booking_schema = spec['components']['schemas']['Booking']
    recording_url = booking_schema['properties']['recording_url']
    desc = str(recording_url.get('description', ''))
    assert 'автоматическ' in desc.lower() or 'генер' in desc.lower() or 'сервер' in desc.lower()


def test_error_schema_has_code_message_errors():
    spec = load_spec()
    error_schema = spec['components']['schemas']['Error']
    assert 'code' in error_schema['properties']
    assert 'message' in error_schema['properties']
    assert 'errors' in error_schema['properties']


def test_all_endpoints_reference_error_schema():
    spec = load_spec()
    for path, methods in spec['paths'].items():
        for method, operation in methods.items():
            if method in ('get', 'post', 'put', 'delete'):
                responses = operation.get('responses', {})
                for status, response in responses.items():
                    if status.startswith('4') or status.startswith('5'):
                        assert '$ref' in response or 'content' in response, (
                           '{method} {path} {status}: отсутствует ссылка на схему ошибки'.format(
                                method=method.upper(), path=path, status=status,
                            )
                        )


def test_conflict_has_slot_already_booked_example():
    spec = load_spec()
    conflict = spec['components']['responses']['Conflict']
    content = conflict.get('content', {})
    json_content = content.get('application/json', {})
    example = json_content.get('example', {})
    assert example.get('code') == 'SLOT_ALREADY_BOOKED'


def test_not_found_has_example():
    spec = load_spec()
    not_found = spec['components']['responses']['NotFound']
    content = not_found.get('content', {})
    json_content = content.get('application/json', {})
    example = json_content.get('example', {})
    assert 'code' in example


def test_bad_request_has_example():
    spec = load_spec()
    bad_request = spec['components']['responses']['BadRequest']
    content = bad_request.get('content', {})
    json_content = content.get('application/json', {})
    example = json_content.get('example', {})
    assert 'code' in example


def test_validation_error_has_examples():
    spec = load_spec()
    validation_error = spec['components']['responses']['ValidationError']
    content = validation_error.get('content', {})
    json_content = content.get('application/json', {})
    examples = json_content.get('examples', {})
    assert len(examples) > 0, 'ValidationError должна содержать примеры ошибок'


def test_datetime_format_uses_rfc3339():
    spec = load_spec()
    booking = spec['components']['schemas']['Booking']
    created_at = booking['properties']['created_at']
    assert created_at.get('format') == 'date-time'
    desc = str(created_at.get('description', ''))
    assert 'RFC 3339' in desc or 'смещени' in desc.lower()


def test_dst_constraints_documented():
    spec = load_spec()
    info_desc = str(spec['info'].get('description', ''))
    assert 'DST' in info_desc or 'летн' in info_desc.lower() or 'переход' in info_desc.lower()


def test_timezone_via_iana_documented():
    spec = load_spec()
    info_desc = str(spec['info'].get('description', ''))
    assert 'IANA' in info_desc or 'tz database' in info_desc or 'часовой пояс' in info_desc.lower()


def test_acceptance_criteria_present():
    spec = load_spec()
    assert 'x-acceptance-criteria' in spec, 'Отсутствуют критерии приёмки'


def test_acceptance_criteria_covers_all_endpoints():
    spec = load_spec()
    criteria = spec.get('x-acceptance-criteria', {})
    paths = spec.get('paths', {})
    for path in paths:
        assert path in criteria, 'Отсутствуют критерии приёмки для {path}'.format(path=path)


def test_acceptance_criteria_use_given_when_then():
    spec = load_spec()
    criteria = spec.get('x-acceptance-criteria', {})
    for path, path_criteria in criteria.items():
        for method, method_criteria in path_criteria.items():
            for criterion in method_criteria:
                assert 'given' in criterion, (
                    '{path} {method}: критерий не содержит Given'.format(path=path, method=method)
                )
                assert 'when' in criterion, (
                    '{path} {method}: критерий не содержит When'.format(path=path, method=method)
                )
                assert 'then' in criterion, (
                    '{path} {method}: критерий не содержит Then'.format(path=path, method=method)
                )


def test_edge_cases_documented():
    spec = load_spec()
    assert 'x-edge-cases' in spec, 'Отсутствуют edge cases'
    edge_cases = spec.get('x-edge-cases', {})
    edge_case_text = str(edge_cases).lower()
    assert 'неверн' in edge_case_text or 'невалидн' in edge_case_text or 'invalid' in edge_case_text
    assert 'падени' in edge_case_text or 'недоступн' in edge_case_text or 'unavailable' in edge_case_text
    assert 'интернет' in edge_case_text or 'network' in edge_case_text or 'offline' in edge_case_text


def test_nfr_documented():
    spec = load_spec()
    assert 'x-nfr' in spec, 'Отсутствуют NFR'
    nfr = spec.get('x-nfr', {})
    nfr_text = str(nfr).lower()
    assert 'производительност' in nfr_text or 'performance' in nfr_text or 'отклик' in nfr_text
    assert 'нагрузк' in nfr_text or 'load' in nfr_text or 'rps' in nfr_text
    assert 'безопасност' in nfr_text or 'security' in nfr_text
    assert 'логир' in nfr_text or 'logging' in nfr_text or 'логов' in nfr_text


def test_migration_strategy_documented():
    spec = load_spec()
    assert 'x-migration-strategy' in spec, 'Отсутствует стратегия миграции'


def test_migration_strategy_describes_coexistence():
    spec = load_spec()
    migration = spec.get('x-migration-strategy', {})
    migration_text = str(migration).lower()
    assert 'сосуществов' in migration_text or 'coexist' in migration_text or 'параллел' in migration_text


def test_migration_strategy_has_phases():
    spec = load_spec()
    migration = spec.get('x-migration-strategy', {})
    assert 'phases' in migration or 'steps' in migration or 'этапы' in migration, (
        'Стратегия миграции должна содержать фазы/этапы'
    )


def test_spec_endpoints_match_django_urls():
    spec = load_spec()
    spec_paths = set(spec.get('paths', {}).keys())
    expected_api_paths = {'/api/slots', '/api/bookings', '/api/bookings/{id}'}
    assert spec_paths == expected_api_paths, (
        'Пути в спецификации не соответствуют ожидаемым API-путям. '
        'Ожидались: {expected}, найдены: {actual}'.format(
            expected=expected_api_paths, actual=spec_paths,
        )
    )


def test_spec_validation_rules_match_booking_form():
    spec = load_spec()
    validation_desc = str(spec['components']['responses']['ValidationError']['description'])
    assert 'выходной день' in validation_desc or 'выходн' in validation_desc
    assert 'кратно 30' in validation_desc
    assert 'рабочие часы' in validation_desc or 'рабочих часов' in validation_desc
    assert 'прошлом' in validation_desc or 'прошедш' in validation_desc
    assert 'занят' in validation_desc


def test_spec_create_booking_required_fields_match_model():
    spec = load_spec()
    create_schema = spec['components']['schemas']['CreateBookingRequest']
    required = set(create_schema.get('required', []))
    expected = {'date', 'time', 'client_name', 'topic', 'meeting_type'}
    assert required == expected, (
        'Обязательные поля в спецификации не соответствуют модели. '
        'Ожидались: {expected}, найдены: {actual}'.format(expected=expected, actual=required)
    )


def test_spec_meeting_type_enum_matches_model():
    spec = load_spec()
    meeting_type = spec['components']['schemas']['MeetingType']
    enum_values = set(meeting_type.get('enum', []))
    expected = {'video', 'audio', 'personal'}
    assert enum_values == expected, (
        'Enum MeetingType в спецификации не соответствует модели. '
        'Ожидались: {expected}, найдены: {actual}'.format(expected=expected, actual=enum_values)
    )


def test_spec_booking_fields_match_model():
    spec = load_spec()
    booking_props = set(spec['components']['schemas']['Booking']['properties'].keys())
    expected = {
        'id', 'date', 'time', 'client_name', 'topic',
        'meeting_type', 'recording_url', 'created_at', 'updated_at',
    }
    assert booking_props == expected, (
        'Поля Booking в спецификации не соответствуют модели. '
        'Ожидались: {expected}, найдены: {actual}'.format(expected=expected, actual=booking_props)
    )
