from unittest.mock import patch

import pytest

from pi0servo.core.calibrable_servo import CalibrableServo
from pi0servo.core.multi_servo import MultiServo

PINS = [17, 18]
CONF_FILE = "test_multi_servo_conf.json"


@pytest.fixture
def mock_calibrable_servo(mocker):
    """
    CalibrableServoのモックを返すフィクスチャ。
    pytest-mockのmockerを使って、CalibrableServoクラス全体をモックする。
    これにより、MultiServoがCalibrableServoのインスタンスを作成する際に、
    実際のCalibrableServoではなく、モックされたインスタンスが使われるようになる。

    なぜモックが必要か：
    MultiServoは内部でCalibrableServoのインスタンスを生成・利用します。
    テストの目的はMultiServo自体のロジックを検証することであり、
    CalibrableServoの内部動作（例：pigpioとの通信）はここでは対象外です。
    CalibrableServoをモックすることで、その依存関係を切り離し、
    MultiServoのテストを独立して、かつ高速に実行できます。
    また、CalibrableServoの特定の振る舞いをシミュレートすることで、
    様々なシナリオ（例：角度の最大値・最小値）を簡単にテストできます。
    """
    # pi0servo.core.multi_servo.CalibrableServo をモックする。
    # autospec=True により、元のクラスのシグネチャを維持し、
    # 存在しない属性へのアクセスを防ぐ。
    mock_cs = mocker.patch(
        "pi0servo.core.multi_servo.CalibrableServo", autospec=True
    )

    # 各サーボに対応するモックインスタンスを作成し、初期値を設定する。
    # これらのモックインスタンスは、MultiServoが内部でCalibrableServoを
    # インスタンス化する際に返される。
    servos = [mocker.MagicMock(spec=CalibrableServo) for _ in PINS]
    for i, s in enumerate(servos):
        # モックインスタンスの属性を設定し、
        # 実際のCalibrableServoの振る舞いを模倣する。
        # 例えば、pinやconf_fileはインスタンスごとに異なる値を持ちうる。
        s.pin = PINS[i]
        s.conf_file = CONF_FILE
        # get_angle()メソッドが呼び出されたときに常に0.0を返すように設定。
        s.get_angle.return_value = 0.0
        # move_angleなどのメソッドは、モックオブジェクトによって
        # 自動的に呼び出しが記録される。特定の返り値を設定しない限り、
        # デフォルトでNoneを返す。テストでは、これらのメソッドが
        # 正しく呼び出されたか（assert_called_withなど）を検証する。
        # プロパティをモックするにはmocker.PropertyMockを使用する。
        # これにより、これらの属性がアクセスされたときに
        # 指定した値を返すようになる。
        # type(s)を使うのは、MagicMockのインスタンスではなく、
        # そのクラス（型）に対してプロパティを設定するため。
        type(s).ANGLE_MAX = mocker.PropertyMock(return_value=90.0)
        type(s).ANGLE_MIN = mocker.PropertyMock(return_value=-90.0)
        type(s).ANGLE_CENTER = mocker.PropertyMock(return_value=0.0)
        type(s).POS_MAX = mocker.PropertyMock(return_value="max")
        type(s).POS_MIN = mocker.PropertyMock(return_value="min")
        type(s).POS_CENTER = mocker.PropertyMock(return_value="center")

    # mock_csが呼び出されるたびに、servosリストから順に
    # モックインスタンスを返すように設定する。
    mock_cs.side_effect = servos
    # モックされたクラスと、作成されたモックインスタンスのリストを返す。
    return mock_cs, servos


@pytest.fixture
def multi_servo(mocker_pigpio, mock_calibrable_servo):
    """
    MultiServoのテスト用インスタンスを生成するフィクスチャ。
    mocker_pigpio: pigpioのモックインスタンス。
    mock_calibrable_servo: CalibrableServoのモッククラスと
    # モックインスタンスのリスト。
    """
    pi = mocker_pigpio()
    # mock_calibrable_servo からモックされたCalibrableServoの
    # インスタンスリストを取得
    _, mock_instances = mock_calibrable_servo
    # MultiServoのインスタンスを作成。
    # first_move=Falseにすることで、初期化時のmove_angle呼び出しを
    # テストから分離し、
    # 各テストで明示的にmove_angleを呼び出すことを可能にする。
    ms = MultiServo(
        pi, PINS, first_move=False, conf_file=CONF_FILE, debug=True
    )
    # MultiServoインスタンスと、モックされたCalibrableServoインスタンスの
    # リストを返す。
    return ms, mock_instances


class TestMultiServo:
    """MultiServoクラスのテスト"""

    def test_init(self, mocker_pigpio, mock_calibrable_servo):
        """
        MultiServoの初期化テスト。
        first_move=Trueの場合に、各サーボが正しく初期化され、
        move_angle(0)が呼び出されることを確認する。
        """
        pi = mocker_pigpio()
        # mock_calibrable_servoフィクスチャから、
        # モックされたCalibrableServoクラスと
        # そのインスタンスリストを取得する。
        mock_class, mock_instances = mock_calibrable_servo

        # first_move=TrueでMultiServoを初期化する。
        # これにより、内部でCalibrableServoのインスタンスが生成され、
        # 各サーボのmove_angle(0)が呼び出されるはず。
        MultiServo(pi, PINS, first_move=True, conf_file=CONF_FILE, debug=True)

        # CalibrableServoがPINSの数だけ呼び出されたことを確認する。
        assert mock_class.call_count == len(PINS)
        # 各ピンに対してCalibrableServoが正しく呼び出されたことを確認する。
        for pin in PINS:
            mock_class.assert_any_call(
                pi, pin, conf_file=CONF_FILE, debug=False
            )

        # first_move=Trueなので、各サーボのmove_angle(0)が
        # 呼ばれたことを確認する。
        for servo_mock in mock_instances:
            servo_mock.move_angle.assert_called_with(0)

    def test_off(self, multi_servo):
        """
        off()メソッドのテスト。
        MultiServoのoff()が呼び出されたときに、
        各CalibrableServoインスタンスのoff()が一度だけ呼び出されることを確認する。
        """
        ms, mock_instances = multi_servo
        ms.off()
        for servo_mock in mock_instances:
            servo_mock.off.assert_called_once()

    def test_getattr_invalid(self, multi_servo):
        """存在しないメソッド呼び出しのテスト"""
        ms, _ = multi_servo
        with pytest.raises(AttributeError):
            ms.invalid_method()

    def test_set_pulse_individual(self, multi_servo):
        """個別サーボのパルス設定テスト"""
        ms, mock_instances = multi_servo

        ms.set_pulse_center(0, 1600)
        assert mock_instances[0].pulse_center == 1600

        ms.set_pulse_min(1, 600)
        assert mock_instances[1].pulse_min == 600

        ms.set_pulse_max(0, 2400)
        assert mock_instances[0].pulse_max == 2400

    def test_move_all_angles(self, multi_servo):
        """
        move_all_anglesのテスト。
        """
        ms, mock_instances = multi_servo
        target_angles = [30, -45]
        ms.move_all_angles(target_angles)
        mock_instances[0].move_angle.assert_called_with(30)
        mock_instances[1].move_angle.assert_called_with(-45)

    def test_get_all_angles(self, multi_servo):
        """
        get_all_anglesのテスト。
        各CalibrableServoインスタンスのget_angle()が呼び出され、
        その戻り値がリストとして正しく返されることを確認する。
        """
        ms, mock_instances = multi_servo
        mock_instances[0].get_angle.return_value = 10.0
        mock_instances[1].get_angle.return_value = -20.0
        angles = ms.get_all_angles()
        assert angles == [10.0, -20.0]

    def test_get_pulse(self, multi_servo):
        """
        get_pulseのテスト。
        """
        ms, mock_instances = multi_servo
        mock_instances[0].get_pulse.return_value = 1500
        pulse = ms.get_pulse(0)
        assert pulse == 1500
        mock_instances[0].get_pulse.assert_called_once()

    def test_get_all_pulses(self, multi_servo):
        """
        get_all_pulsesのテスト。
        """
        ms, mock_instances = multi_servo
        mock_instances[0].get_pulse.return_value = 1500
        mock_instances[1].get_pulse.return_value = 1600
        pulses = ms.get_all_pulses()
        assert pulses == [1500, 1600]
        mock_instances[0].get_pulse.assert_called_once()
        mock_instances[1].get_pulse.assert_called_once()

    def test_move_pulse(self, multi_servo):
        """
        move_pulseのテスト。
        """
        ms, mock_instances = multi_servo
        ms.move_pulse(0, 1500)
        mock_instances[0].move_pulse.assert_called_once_with(1500, False)

    def test_move_all_pulses(self, multi_servo):
        """
        move_all_pulsesのテスト。
        """
        ms, mock_instances = multi_servo
        pulses = [1500, 1600]
        ms.move_all_pulses(pulses)
        mock_instances[0].move_pulse.assert_called_once_with(1500, False)
        mock_instances[1].move_pulse.assert_called_once_with(1600, False)

    def test_move_pulse_relative(self, multi_servo):
        """
        move_pulse_relativeのテスト。
        """
        ms, mock_instances = multi_servo
        mock_instances[0].get_pulse.return_value = 1500
        ms.move_pulse_relative(0, 100)
        mock_instances[0].get_pulse.assert_called_once()
        mock_instances[0].move_pulse.assert_called_once_with(1600, False)

    def test_move_all_pulses_relative(self, multi_servo):
        """
        move_all_pulses_relativeのテスト。
        """
        ms, mock_instances = multi_servo
        mock_instances[0].get_pulse.return_value = 1500
        mock_instances[1].get_pulse.return_value = 1600
        pulse_diffs = [100, -100]
        ms.move_all_pulses_relative(pulse_diffs)
        mock_instances[0].get_pulse.assert_called_once()
        mock_instances[1].get_pulse.assert_called_once()
        mock_instances[0].move_pulse.assert_called_once_with(1600, False)
        mock_instances[1].move_pulse.assert_called_once_with(1500, False)

    def test_validate_angle_list_invalid_type(self, multi_servo):
        """
        _validate_angle_listの不正な型に対するテスト。
        """
        ms, _ = multi_servo
        assert ms._validate_angle_list("not a list") is False
        assert ms._validate_angle_list(123) is False

    def test_validate_angle_list_invalid_length(self, multi_servo):
        """
        _validate_angle_listの不正な長さに対するテスト。
        """
        ms, _ = multi_servo
        assert ms._validate_angle_list([10]) is False  # 1要素
        assert ms._validate_angle_list([10, 20, 30]) is False  # 3要素

    @patch("time.sleep")
    def test_move_all_angles_sync_relative(self, mock_sleep, multi_servo):
        """
        move_all_angles_sync_relativeのテスト。
        複数のサーボが指定された角度まで同期して滑らかに動くことを確認する。
        """
        ms, mock_instances = multi_servo

        start_angles = [0, 0]
        angle_diffs = [30, -45]
        steps = 10
        move_sec = 0.5

        for i, servo_mock in enumerate(mock_instances):
            servo_mock.get_angle.return_value = start_angles[i]

        ms.move_all_angles_sync_relative(
            angle_diffs, move_sec=move_sec, step_n=steps
        )

        assert mock_instances[0].move_angle.call_count == steps
        assert mock_instances[1].move_angle.call_count == steps

        for i in range(steps):
            # 途中の角度が線形補間されていることを確認
            expected_angle0 = (
                start_angles[0] + angle_diffs[0] * (i + 1) / steps
            )
            mock_instances[0].move_angle.assert_any_call(expected_angle0)

            expected_angle1 = (
                start_angles[1] + angle_diffs[1] * (i + 1) / steps
            )
            mock_instances[1].move_angle.assert_any_call(expected_angle1)

        # 最後の呼び出しは目標角度になっているはず
        mock_instances[0].move_angle.assert_called_with(
            start_angles[0] + angle_diffs[0]
        )
        mock_instances[1].move_angle.assert_called_with(
            start_angles[1] + angle_diffs[1]
        )

        assert mock_sleep.call_count == steps
        mock_sleep.assert_called_with(move_sec / steps)

    @patch("time.sleep")
    def test_move_all_angles_sync(self, mock_sleep, multi_servo):
        """
        move_all_angles_syncメソッドのテスト。
        複数のサーボが指定された角度まで同期して滑らかに動くことを確認する。
        time.sleepをモックすることで、テストの実行時間を短縮し、
        実際の時間経過を待たずにテストを完了させる。
        """
        ms, mock_instances = multi_servo

        start_angles = [0, 0]
        target_angles = [90, -90]
        steps = 10
        move_sec = 0.5

        # 各サーボの現在の角度を設定する。
        for i, servo_mock in enumerate(mock_instances):
            servo_mock.get_angle.return_value = start_angles[i]

        # move_all_angles_syncを呼び出す。
        ms.move_all_angles_sync(
            target_angles, move_sec=move_sec, step_n=steps
        )

        # 各サーボのmove_angleがsteps回呼び出されたことを確認する。
        assert mock_instances[0].move_angle.call_count == steps
        assert mock_instances[1].move_angle.call_count == steps

        # 各ステップでの角度が線形補間されていることを確認する。
        for i in range(steps):
            expected_angle0 = (
                start_angles[0]
                + (target_angles[0] - start_angles[0]) * (i + 1) / steps
            )
            mock_instances[0].move_angle.assert_any_call(expected_angle0)

            expected_angle1 = (
                start_angles[1]
                + (target_angles[1] - start_angles[1]) * (i + 1) / steps
            )
            mock_instances[1].move_angle.assert_any_call(expected_angle1)

        # 最後の呼び出しが目標角度であることを確認する。
        mock_instances[0].move_angle.assert_called_with(target_angles[0])
        mock_instances[1].move_angle.assert_called_with(target_angles[1])

        # time.sleepがsteps回呼び出され、
        # 正しい引数で呼び出されたことを確認する。
        assert mock_sleep.call_count == steps
        mock_sleep.assert_called_with(move_sec / steps)

    @patch("time.sleep")
    def test_move_all_angles_sync_str_none(self, mock_sleep, multi_servo):
        """
        move_all_angles_syncのテスト（文字列とNoneを含む）。
        """
        ms, mock_instances = multi_servo
        start_angles = [10, 20]
        target_angles = ["max", None]
        steps = 10

        for i, servo_mock in enumerate(mock_instances):
            servo_mock.get_angle.return_value = start_angles[i]

        ms.move_all_angles_sync(target_angles, step_n=steps)

        # "max"が角度90.0に変換される
        mock_instances[0].move_angle.assert_called_with(90.0)
        assert mock_instances[0].move_angle.call_count == steps

        # Noneは現在の角度維持
        mock_instances[1].move_angle.assert_called_with(start_angles[1])
        assert mock_instances[1].move_angle.call_count == steps

        # サーボ0の途中の角度が線形補間されていることを確認
        for i in range(steps):
            expected_angle = (
                start_angles[0] + (90.0 - start_angles[0]) * (i + 1) / steps
            )
            mock_instances[0].move_angle.assert_any_call(expected_angle)

    @patch("time.sleep")
    def test_move_all_angles_sync_invalid_str(self, mock_sleep, multi_servo):
        """
        move_all_angles_syncの不正な文字列引数に対するテスト。
        """
        ms, mock_instances = multi_servo
        start_angles = [10, 20]
        target_angles = ["invalid", None]
        steps = 10

        for i, servo_mock in enumerate(mock_instances):
            servo_mock.get_angle.return_value = start_angles[i]

        ms.move_all_angles_sync(target_angles, step_n=steps)

        # "invalid"は現在の角度維持
        mock_instances[0].move_angle.assert_called_with(start_angles[0])
        assert mock_instances[0].move_angle.call_count == steps

        # Noneは現在の角度維持
        mock_instances[1].move_angle.assert_called_with(start_angles[1])
        assert mock_instances[1].move_angle.call_count == steps

    def test_move_all_angles_sync_direct(self, multi_servo):
        """
        move_all_angles_syncのテスト（step_n=1）。
        """
        ms, mock_instances = multi_servo
        target_angles = [30, -45]
        ms.move_all_angles_sync(target_angles, step_n=1)

        mock_instances[0].move_angle.assert_called_once_with(30)
        mock_instances[1].move_angle.assert_called_once_with(-45)
