# Tic-Tac-Toe (〇×ゲーム)

Windows11 + Python 3.14 で動作する 3x3 の〇×ゲームです。

## 必要環境

- Windows 11
- Python 3.14
- tkinter（Python標準ライブラリ）

## セットアップ

1. リポジトリをクローンまたはダウンロード

2. （オプション）OpenAI APIを使用する場合は、`.env`ファイルを作成してAPIキーを設定:
   ```
   cp .env.example .env
   # .env ファイルを編集してAPIキーを設定
   ```

3. 依存パッケージをインストール（OpenAI機能を使う場合のみ必要）:
   ```
   pip install -r requirements.txt
   ```

## 起動方法

```bash
cd D:\python\marubatu
python main.py
```

## 操作方法

1. **開始ボタン**: ゲームを開始します。先手（CPU or 人間）はランダムに決まります。
2. **マスをクリック**: 人間の手番でマスをクリックして手を置きます。
3. **リセットボタン**: ゲームをリセットして初期状態に戻します。

## ゲームルール

- 3x3のマスに交互に「X」と「O」を置きます
- 先に縦・横・斜めのいずれかで3つ揃えた方が勝ち
- 全マスが埋まっても勝者がいない場合は引き分け

## CPUの思考ロジック

CPUは以下の優先順位で手を決定します：

1. 勝てる手があれば勝つ
2. 相手の勝ちを阻止できるなら阻止
3. 中心を取る
4. 角を取る
5. 辺を取る

## ログ機能

ゲームの履歴は `logs/` フォルダに自動保存されます。

- ファイル名: `session_YYYYMMDD_HHMMSS.jsonl`
- 形式: JSON Lines（1行1ゲーム）
- 記録内容: 開始日時、先手、手順、勝者、終了日時

## OpenAI連携（オプション）

`.env`ファイルに`OPENAI_API_KEY`を設定すると、以下の機能が有効になります：

- CPUの手の候補生成（失敗時はローカルロジックにフォールバック）
- 対戦後の反省コメント表示

**注意**: OpenAI APIが使えない環境でもゲームは正常に動作します。

## ファイル構成

```
D:\python\marubatu\
├── main.py              # 起動エントリ
├── game/
│   ├── __init__.py
│   ├── board.py         # 盤面管理
│   ├── judge.py         # 勝敗判定
│   └── cpu.py           # CPUロジック
├── ui/
│   ├── __init__.py
│   └── app.py           # tkinter GUI
├── logs/                # ゲームログ（自動生成）
├── .env.example         # 環境変数サンプル
├── .gitignore
├── requirements.txt
└── README.md
```

## ライセンス

MIT License
