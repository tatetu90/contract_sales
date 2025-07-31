import streamlit as st
import pandas as pd

# データ読み込み
df = pd.read_excel("Q1_contract.xlsx", sheet_name='Sheet1')

# 契約日を月単位に加工
df['契約日'] = pd.to_datetime(df['契約日'])
df['契約月'] = df['契約日'].dt.to_period('M').astype(str)

# 年収を「百万単位」に変換し、100万円刻みのレンジを作成
df['年収_百万'] = df['本人年収（万単位）'] / 100
max_income = int(df['年収_百万'].max()) + 1
income_bins = list(range(0, max_income + 1, 1))
income_labels = [f"{i}～{i+1}百万" for i in income_bins[:-1]]
df['年収レンジ'] = pd.cut(df['年収_百万'], bins=income_bins, labels=income_labels, right=False)

# 年齢を5歳刻みのレンジに加工
min_age = int(df['年齢'].min() // 5 * 5)
max_age = int((df['年齢'].max() // 5 + 1) * 5)
age_bins = list(range(min_age, max_age + 5, 5))
age_labels = [f"{i}～{i+5}歳" for i in age_bins[:-1]]
df['年齢レンジ'] = pd.cut(df['年齢'], bins=age_bins, labels=age_labels, right=False)

# サイドバーフィルタ設定（複数選択可）
st.sidebar.header("フィルタ設定")
prefectures = st.sidebar.multiselect('都道府県', df['都道府県名'].unique(), df['都道府県名'].unique())
genders = st.sidebar.multiselect('性別', df['性別'].unique(), df['性別'].unique())
occupations = st.sidebar.multiselect('職業区分', df['職業区分'].unique(), df['職業区分'].unique())
contract_months = st.sidebar.multiselect('契約月', sorted(df['契約月'].unique()), sorted(df['契約月'].unique()))
income_ranges = st.sidebar.multiselect('年収レンジ', income_labels, income_labels)
age_ranges = st.sidebar.multiselect('年齢レンジ', age_labels, age_labels)

# フィルタ適用
filtered = df[
    df['都道府県名'].isin(prefectures) &
    df['性別'].isin(genders) &
    df['職業区分'].isin(occupations) &
    df['契約月'].isin(contract_months) &
    df['年収レンジ'].isin(income_ranges) &
    df['年齢レンジ'].isin(age_ranges)
]

# ダッシュボード表示
st.title("入居者属性による月額利用料")
st.write(f"フィルタ後のデータ件数：{len(filtered)}件")

# 平均値計算
metrics = filtered.agg({
    '家賃': 'mean',
    '共益費': 'mean',
    '環境維持費': 'mean',
    'インターネット': 'mean',
    '月額利用料': 'mean',
    '抗菌施行販売金額': 'mean'
}).rename(lambda x: '平均' + x)

# 駐車場の平均値計算（値が0ではないもののみ）
parking_filtered = filtered[filtered['駐車場'] > 0]
parking_mean = parking_filtered['駐車場'].mean()
metrics['平均駐車場'] = parking_mean

# 抗菌施行販売金額の利用者数計算
antibacterial_usage_count = (filtered['抗菌施行販売金額'] > 0).sum()

# 駐車場利用者数計算
parking_usage_count = len(parking_filtered)

# 数値表示
st.subheader("平均値")
for label, value in metrics.items():
    st.metric(label, f"{value:,.0f}円")
    if label == '平均抗菌施行販売金額':
        st.write(f"抗菌施行販売金額の値が0ではない人の人数: {antibacterial_usage_count}人")
    if label == '平均駐車場':
        st.write(f"駐車場利用者数: {parking_usage_count}人")

# 最大値計算
max_metrics = filtered.agg({
    '月額利用料': 'max',
    '抗菌施行販売金額': 'max'
}).rename(lambda x: '最大' + x)

# 最大値表示
st.subheader("最大支払可能金額")
for label, value in max_metrics.items():
    st.metric(label, f"{value:,.0f}円")

# 棒グラフ
st.subheader("平均値の棒グラフ")
st.bar_chart(metrics)

st.subheader("最大値の棒グラフ")
st.bar_chart(max_metrics)
