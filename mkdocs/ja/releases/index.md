Releases
========

主なリリース情報を記載します。  
全ての変更はGitHubのコミットログをご覧ください。

## :package: 0.32.0

:fa-calendar: `2017/12/19`

??? info "richplainアドオンを追加しました ([res2dict/richplain])"
    
    * 特殊な形式で記載されたテキストをdictに変換することができます
    * 詳細は [res2dict/richplain] をご覧ください


## :package: 0.31.1

:fa-calendar: `2017/12/19`

??? hint "レスポンスヘッダにエンコーディング情報が無い場合、UTF8ではなく推測したエンコーディングでデコードするようにしました"
    
    APIにリクエストした結果(body)をUnicodeへデコードする場合の話です


## :package: 0.31.0

:fa-calendar: `2017/12/14`

??? hint "リクエスト結果が返却された後の処理を高速化しました"
    
    レスポンスサイズが大きく、結果がほぼSameの場合は10倍以上速くなるケースもあります


## :package: 0.30.1

:fa-calendar: `2017/12/06`

!!! hint "when_notプロパティをwhenに変更しました ([final/miroir])"


[res2dict/richplain]: /ja/addons/res2dict#richplain
[final/miroir]: /ja/addons/final#miroir