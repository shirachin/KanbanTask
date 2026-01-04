<template>
  <div class="help">
    <div class="help-header">
      <h2>使い方</h2>
    </div>
    
    <div class="help-content">
      <section class="help-section">
        <h3 class="section-title">ログイン</h3>
        <p class="section-description">
          アプリを起動すると、ログイン画面が表示されます。半角英数字のみのユーザー名を入力してログインしてください。ログインしたユーザー名は自動的に保存され、次回起動時にも保持されます。
        </p>
      </section>

      <section class="help-section">
        <h3 class="section-title">ダッシュボード</h3>
        <p class="section-description">
          ダッシュボードでは、プロジェクト一覧やタスクの統計情報を確認できます（現在は簡易的な表示のみ）。
        </p>
      </section>

      <section class="help-section">
        <h3 class="section-title">カンバンボード</h3>
        <div class="section-description">
          <p>カンバンボードでは、タスクをステータスごとに管理できます。</p>
          <h4 class="subsection-title">プロジェクトモード選択</h4>
          <ul class="feature-list">
            <li><strong>自身が担当するすべてのプロジェクト+個人的タスク</strong>: 自分が担当するすべてのプロジェクトと個人的タスクを表示します。</li>
            <li><strong>プロジェクト検索（自分の担当プロジェクト）</strong>: 検索機能を使用して特定のプロジェクトを選択できます。プロジェクト名を入力すると、リアルタイムでフィルタリングされます。キーボードの上下矢印キーで選択肢を移動し、Enterキーで選択できます。選択後は担当者でフィルタリングすることもできます。</li>
            <li><strong>個人的タスク</strong>: 個人タスクのみを表示します。</li>
          </ul>
          <h4 class="subsection-title">タスクの操作</h4>
          <ul class="feature-list">
            <li><strong>タスクの追加</strong>: 右上の「タスク追加」ボタンをクリックして、新しいタスクを作成できます。タスク作成モーダルでは、プロジェクト選択がオートコンプリート形式になっており、プロジェクト名を入力して検索できます。キーボードの上下矢印キーで選択肢を移動し、Enterキーで選択できます。</li>
            <li><strong>タスクの編集</strong>: タスクカードをクリックすると編集モーダルが開き、タスク名、説明、ステータス、担当者などを変更できます。</li>
            <li><strong>ステータスの変更</strong>: タスク編集モーダルでステータスを選択して変更できます。</li>
            <li><strong>TODOの追加</strong>: タスクカード内の「+ TODOを追加」欄にテキストを入力し、Enterキーを押すか、入力欄からフォーカスを外すとTODOが追加されます。</li>
            <li><strong>TODOの削除</strong>: TODO項目の右側にある削除ボタンをクリックして削除できます。</li>
            <li><strong>TODOの完了状態</strong>: TODOの完了状態は実行完了日で自動管理されます。手動での切り替えはできません。</li>
          </ul>
        </div>
      </section>

      <section class="help-section">
        <h3 class="section-title">TODOリスト</h3>
        <div class="section-description">
          <p>TODOリストでは、すべてのタスクのTODOを一覧表示し、管理できます。</p>
          <h4 class="subsection-title">表示機能</h4>
          <ul class="feature-list">
            <li><strong>グリッド表示</strong>: AG Gridを使用した表形式で表示されます。</li>
            <li><strong>カラム</strong>: 完了状態、TODO、タスク名、プロジェクト名、予定日、実行完了日が表示されます。</li>
            <li><strong>完了状態の切り替え</strong>: チェックボックスをクリックして、TODOの完了状態を切り替えられます。</li>
          </ul>
          <h4 class="subsection-title">フィルタとソート</h4>
          <ul class="feature-list">
            <li><strong>フィルタテンプレート</strong>: 画面上部の「フィルタテンプレート」ボタンから、事前定義されたフィルタとソート条件を適用できます。ボタンにマウスオーバーすると、適用されるフィルタ設定がツールチップで表示されます。「リセット」ボタンをクリックすると、すべてのフィルタとソートがクリアされます。</li>
            <li><strong>カラムフィルタ</strong>: 各カラムのヘッダーにフィルタアイコンをクリックして、カラムごとにフィルタを設定できます。</li>
            <li><strong>ソート</strong>: カラムヘッダーをクリックして、昇順・降順でソートできます。複数のカラムでソートすることも可能です。</li>
            <li><strong>状態の保存</strong>: 設定したフィルタ、ソート、ページサイズ、カラムの幅や表示/非表示は自動的にLocalStorageに保存され、次回アクセス時にも保持されます。</li>
          </ul>
          <h4 class="subsection-title">ページネーション</h4>
          <ul class="feature-list">
            <li>画面下部のページネーションコントロールで、1ページあたりの表示件数（25、50、100、200件）を選択できます。</li>
          </ul>
        </div>
      </section>

      <section class="help-section">
        <h3 class="section-title">プロジェクト管理</h3>
        <div class="section-description">
          <p>プロジェクト管理では、プロジェクトの作成、編集、削除ができます。</p>
          <h4 class="subsection-title">プロジェクトの操作</h4>
          <ul class="feature-list">
            <li><strong>プロジェクトの追加</strong>: 右上の「プロジェクト追加」ボタンをクリックして、新しいプロジェクトを作成できます。</li>
            <li><strong>プロジェクトの編集</strong>: グリッドの「編集」ボタンをクリックして、プロジェクト情報を編集できます。</li>
            <li><strong>プロジェクトの削除</strong>: グリッドの「削除」ボタンをクリックして、プロジェクトを削除できます。削除前に確認ダイアログが表示されます。</li>
            <li><strong>担当者の管理</strong>: プロジェクトには複数の担当者を設定できます。担当者はカンマ区切りで入力します。</li>
          </ul>
          <h4 class="subsection-title">フィルタとソート</h4>
          <ul class="feature-list">
            <li><strong>カラムフィルタ</strong>: 各カラムのヘッダーにフィルタアイコンをクリックして、カラムごとにフィルタを設定できます。</li>
            <li><strong>ソート</strong>: カラムヘッダーをクリックして、昇順・降順でソートできます。</li>
            <li><strong>状態の保存</strong>: 設定したフィルタ、ソート、ページサイズ、カラムの幅や表示/非表示は自動的にLocalStorageに保存され、次回アクセス時にも保持されます。</li>
          </ul>
          <h4 class="subsection-title">ページネーション</h4>
          <ul class="feature-list">
            <li>画面下部のページネーションコントロールで、1ページあたりの表示件数（25、50、100、200件）を選択できます。</li>
          </ul>
        </div>
      </section>

      <section class="help-section">
        <h3 class="section-title">ガントチャート</h3>
        <p class="section-description">
          ガントチャート機能は現在未実装です。今後実装予定です。
        </p>
      </section>

      <section class="help-section">
        <h3 class="section-title">テーマ切り替え</h3>
        <p class="section-description">
          ヘッダー右上のカラーアイコンをクリックすると、テーマを切り替えることができます。選択したテーマは自動的にLocalStorageに保存され、次回アクセス時にも保持されます。
        </p>
      </section>

      <section class="help-section">
        <h3 class="section-title">ナビゲーション</h3>
        <p class="section-description">
          ヘッダー左上のメニューアイコンをクリックすると、ナビゲーションを開閉できます。ナビゲーションの最下部には、現在ログイン中のユーザー名が表示されます。選択中のページはハイライト表示されます。
        </p>
      </section>

      <section class="help-section">
        <h3 class="section-title">ログアウト</h3>
        <p class="section-description">
          ナビゲーション最下部のユーザー情報をクリックすると、ログアウトメニューが表示されます。ログアウトボタンをクリックしてログアウトできます。ログアウト後は、ログイン画面に戻ります。
        </p>
      </section>

      <section class="help-section">
        <h3 class="section-title">データの保存</h3>
        <p class="section-description">
          以下の設定は自動的にLocalStorageに保存され、次回アクセス時にも保持されます：
        </p>
        <ul class="feature-list">
          <li>ログインユーザー名</li>
          <li>現在表示中のページ</li>
          <li>テーマ設定</li>
          <li>カンバンボードのプロジェクトモードと選択状態</li>
          <li>TODOリストのフィルタ、ソート、ページサイズ、カラム状態</li>
          <li>プロジェクト管理のフィルタ、ソート、ページサイズ、カラム状態</li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
// 使い方ページのロジックをここに追加
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.help {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.help-header {
  margin-bottom: 2rem;

  h2 {
    margin: 0;
    color: var(--current-textPrimary);
    font-size: 2rem;
    font-weight: 600;
  }
}

.help-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.help-section {
  background: var(--current-backgroundLight);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px var(--current-shadowMd);
}

.section-title {
  margin: 0 0 0.75rem 0;
  color: var(--current-textPrimary);
  font-size: 1.25rem;
  font-weight: 600;
}

.section-description {
  margin: 0;
  color: var(--current-textPrimary);
  line-height: 1.8;

  p {
    margin: 0 0 1rem 0;

    &:last-child {
      margin-bottom: 0;
    }
  }
}

.subsection-title {
  margin: 1.5rem 0 0.75rem 0;
  color: var(--current-textPrimary);
  font-size: 1rem;
  font-weight: 600;

  &:first-child {
    margin-top: 0;
  }
}

.feature-list {
  margin: 0.75rem 0 0 1.5rem;
  padding: 0;
  color: var(--current-textPrimary);
  line-height: 1.8;

  li {
    margin-bottom: 0.5rem;

    &:last-child {
      margin-bottom: 0;
    }

    strong {
      font-weight: 600;
    }
  }
}
</style>
