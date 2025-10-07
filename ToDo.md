  - [x] 'tests/test_04_multi_servo.py'を精読して、よりシンプルでわかり易くならないか検討する。
      - まだ、コードは修正しないこと。
      - 'Plan.md'に方針をステップバイステップでまとめて。
  - [x] 'Plan.md'に基づいて、タスクを検討し、細分化して、ステップバイステップで進められるように、チェックリストを'Tasks.md'として作成する。
  - [x] 'src/pi0servo/core/multi_servo.py'を精読して、'tests/test_04_multi_servo.py'のテスト内容を検討して、'tests/test_04_multi_servo.py'を修正する。
    - 不要なテストを削除。
    - 必要なテストを追加。
    - 'src/pi0servo/core/multi_servo.py'は、修正しないこと。
  - [x] pytest,mockの使い方になれてない人でもわかるように、'src/pi0servo/core/multi_servo.py'にコメントとして解説を追記してください。
  - [x] 'mock_calibrable_servo'について、これで、なぜ、実際のCalibrableServoの代わりになるのか、もう少し解説コメントを追記してください。
  - [x] 'mock_calibrable_servo'について、このモックがどのように、実際のCalibrableServoの動作をシミュレートしているのか、今後、ユーザーが自分でモックを作る際に参考になるように、解説コメントを追記してください。
  - [x] MultiServo内部では、CalibrableServoのメソッドを呼び出しているが、それらの振る舞いは、どのようにシミュレートされるのか、説明コメントを追記してください。
  - [x] CalibrableServoのget_methodがシミュレートされるのは理解したが、例えば、'move_angle'メソッドについては何も書かれていないように見えるが、どのようにシミュレートされるのか、説明コメントを追記してください。





