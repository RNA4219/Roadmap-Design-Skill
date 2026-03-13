# AIエージェント構築サンプル要件

## 目的

個人または小規模チームが、ローカル文書と外部ツールを扱える AI エージェントを段階的に作れるようにしたい。

## 期待する最小成果

- テキスト要求から計画を立てられる
- validate と run の契約が分かれている
- CLI / HTTP / MCP で同じ request / response 形状を共有している
- サンプル入力と出力が残り、再現できる

## 制約

- まずは同期 MVP に限定する
- 1リクエスト1課題を維持する
- 小さなチームで 2 週間以内に最小版を形にしたい
- 後から memory や tool routing を伸ばせる形にしたい

## 利用可能資産

- 既存の README / requirements / specification / interfaces
- deterministic planner の実装
- CLI / HTTP / MCP の薄い wrapper
- 既存の contract / unit / integration test

## 既知の失敗

- 要件定義と I/F を先に固定しないと、後から wrapper ごとの差分修正が増える
- サンプル出力が弱いと、使い方の理解が進まない
