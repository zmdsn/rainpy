from scipy.stats import norm, shapiro, anderson, kstest
from scipy.stats import shapiro
from scipy.stats import multivariate_normal
from sklearn.covariance import EllipticEnvelope
import base64
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
from sklearn.discriminant_analysis import StandardScaler
from sklearn.neighbors import LocalOutlierFactor
import numpy as np
import pandas as pd
from scipy import stats

from rainpy import read


def quick_timestamp_check(value):
    """
    快速判断单个值是否为时间戳
    """
    value = float(value)

    # 常见时间戳范围判断
    if 1e9 <= value <= 2e9:
        return "s"
    elif 1e12 <= value <= 2e13:
        return "ms"
    elif 1e15 <= value <= 2e16:
        return "us"
    elif 10000000 <= value <= 29991231:
        return "YYYYMMDD"
    elif 3560 <= value <= 50000:
        return "可能是Excel日期"
    else:
        return False


def quick_timestamp_check_series(df):
    checks = df.apply(lambda x: quick_timestamp_check(x))
    return checks.mode()[0]


def _score_time_column(df, col, sample_size=20):
    """
    对单列计算时间列评分，返回 (score, reasons)
    """
    score = 0
    reasons = []

    # 1. 列名提示
    time_keywords = ['time', 'date', 'timestamp',
                     'datetime', 'created', 'updated']
    if any(keyword in col.lower() for keyword in time_keywords):
        score += 10
        reasons = "keyword"

    # 2. 已是 datetime 类型 或 可转换为 datetime
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        score += 50
        reasons = "datetime"
    elif df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
        sample = df[col].head(sample_size).dropna()
        if not sample.empty:
            try:
                converted = pd.to_datetime(sample, errors='coerce')
                # 若至少一半样本可转换，则认为可转换为时间
                if converted.notna().sum() >= max(1, int(len(sample) * 0.5)):
                    score += 50
                    reasons = "to_datetime"
            except:
                pass

    # 3. 高唯一性提示
    if len(df) > 0 and df[col].nunique() / len(df) > 0.8:
        score += 10

    # 4. 值范围检查（数值型）
    if pd.api.types.is_integer_dtype(df[col]) or pd.api.types.is_float_dtype(df[col]):
        sample_vals = df[col].dropna().head(sample_size)
        if not sample_vals.empty:
            checks = sample_vals.apply(lambda x: quick_timestamp_check(x))
            # 返回出现频率最高的值
            if checks.all():
                score += 30
                reasons = checks.mode()[0]
    return score, reasons


def get_datetime_column(df, sample_size=50):
    """
    综合性的时间列检测，返回置信度最高的列名或 None
    """
    results = []
    for col in df.columns:
        score, reasons = _score_time_column(df, col, sample_size)
        if score > 0:
            results.append((col, score, reasons))
    if results:
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        if sorted_results[0][1] > 10:
            return sorted_results[0]
        raise ValueError("未检测到时间字段")
    else:
        # 未检测到时间列，按照函数文档返回 None
        raise ValueError("未检测到时间字段")


def set_datetime_index(df, datetime_col=None):
    if datetime_col:
        ds_type = quick_timestamp_check_series(df[datetime_col].head(20))
        if ds_type in ['s', 'ms', 'us']:
            df[datetime_col] = pd.to_datetime(df[datetime_col], unit=ds_type)
        else:
            df[datetime_col] = pd.to_datetime(df[datetime_col])
        df.set_index(datetime_col, inplace=True)
    else:
        datetime_col, _,  ds_type = get_datetime_column(df)
        if datetime_col:
            if ds_type in ['s', 'ms', 'us']:
                df[datetime_col] = pd.to_datetime(
                    df[datetime_col], unit=ds_type)
            else:
                df[datetime_col] = pd.to_datetime(df[datetime_col])
            df.set_index(datetime_col, inplace=True)
    return df


def read_data(file_path):
    df = read(file_path)
    df = set_datetime_index(df)
    return df


def describe(df):
    """
    产生描述性统计数据
    """
    if isinstance(df, str):
        df = read_data(df)
    return df.describe().to_json()


def is_uniform_sampling(df):
    """
    检查数据是否为均匀采样
    """
    if isinstance(df, str):
        df = read_data(df)
    if df.shape[0] > 2:
        time_diff = df.index.to_series().diff()
        return len(time_diff[1:].unique()) == 1
    return True

# 是否缺失数据


def has_missing_data(df):
    """
    检查数据是否存在缺失
    """
    if isinstance(df, str):
        df = read_data(df)
    if df.isnull().values.any():
        return True
    return False

# 是否存在重复时间戳


def has_duplicate_timestamps(df):
    """
    检查数据是否存在重复时间戳
    """
    if isinstance(df, str):
        df = read_data(df)
    if df.index.duplicated().any():
        return True
    return False

# 是否时间索引连续


def is_time_index_continuous(df):
    """
    检查时间索引是否连续
    """
    if isinstance(df, str):
        df = read_data(df)
    time_diff = df.index.to_series().diff().dropna()
    expected_diff = time_diff.mode()[0]
    discontinuities = time_diff[time_diff != expected_diff]
    if not discontinuities.empty:
        return False
    return True


def resample_time_series(df, freq):
    """
    重采样时间序列数据
    """
    if isinstance(df, str):
        df = read_data(df)
    df_resampled = df.resample(freq).mean()
    return df_resampled


def fill_missing_timestamps(df, method='ffill'):
    """
    填充缺失的时间戳
    """
    if isinstance(df, str):
        df = read_data(df)
    full_range = pd.date_range(start=df.index.min(),
                               end=df.index.max(), freq=pd.infer_freq(df.index))
    df_reindexed = df.reindex(full_range)
    if method == 'ffill':
        df_filled = df_reindexed.ffill()
    elif method == 'bfill':
        df_filled = df_reindexed.bfill()
    elif method == 'interpolate':
        df_filled = df_reindexed.interpolate()
    else:
        raise ValueError("Unsupported fill method")
    return df_filled


def z_score_detection(series, threshold=3, show=False):
    """
    Z-Score点异常检测,适用于近似正态分布的数据
    """
    # 计算Z-Score
    z_scores = np.abs(stats.zscore(series))

    # 检测异常
    anomalies_mask = z_scores > threshold
    anomalies = series[anomalies_mask]

    image_base64 = None
    if show:
        plt.figure(figsize=(12, 6))
        plt.plot(series.index, series.values, label='raw score', alpha=0.7)
        plt.scatter(anomalies.index, anomalies.values, color='red',
                    label=f'Z-Score (threshold={threshold})', s=50)
        plt.title('Z-Score Anomaly Detection')
        plt.legend()

        # 将图像转换为字节流
        img = BytesIO()
        plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        img.seek(0)

        # 将字节流转换为 Base64 字符串
        image_base64 = base64.b64encode(img.read()).decode('utf-8')

    return anomalies, image_base64


def iqr_detection(series, multiplier=1.5, show=False):
    """
    IQR点异常检测
    对非正态分布和偏态分布更鲁棒
    """
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR

    anomalies = series[(series < lower_bound) | (series > upper_bound)]

    image_base64 = None
    if show:
        plt.figure(figsize=(12, 6))
        plt.plot(series.index, series.values, label='raw score', alpha=0.7)
        plt.axhline(y=lower_bound, color='r',
                    linestyle='--', alpha=0.7, label='bounds')
        plt.axhline(y=upper_bound, color='r', linestyle='--', alpha=0.7)
        plt.axhline(y=Q1, color='gray', linestyle=':',
                    alpha=0.5, label='Q1/Q3')
        plt.axhline(y=Q3, color='gray', linestyle=':', alpha=0.5)
        plt.scatter(anomalies.index, anomalies.values, color='red',
                    label=f'IQR (multiplier={multiplier})', s=50)
        plt.title('IQR Anomaly Detection')
        plt.legend()

        # 将图像转换为字节流
        img = BytesIO()
        plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        img.seek(0)

        # 将字节流转换为 Base64 字符串
        image_base64 = base64.b64encode(img.read()).decode('utf-8')

    return anomalies, image_base64


def lof_detection(series, n_neighbors=20, contamination=0.05, show=False):
    """
    局部离群因子异常检测
    """
    # 准备特征
    values = series.values.reshape(-1, 1)
    hours = series.index.hour.values.reshape(-1, 1)

    features = np.hstack([values, hours])
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # LOF检测
    lof = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=contamination,
        novelty=False
    )

    anomalies_labels = lof.fit_predict(features_scaled)
    anomalies_mask = anomalies_labels == -1
    anomalies = series[anomalies_mask]

    # 计算异常分数
    anomaly_scores = -lof.negative_outlier_factor_

    image_base64 = None
    if show:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # 异常点可视化
        ax1.plot(series.index, series.values, label='raw data', alpha=0.7)
        ax1.scatter(anomalies.index, anomalies.values, color='red',
                    label='LOF Detection', s=50)
        ax1.set_title(f'LOF Anomaly Detection (neighbors={n_neighbors})')
        ax1.legend()

        # 异常分数可视化
        ax2.plot(series.index, anomaly_scores, 'g-',
                 alpha=0.7, label='Detection Score')
        ax2.axhline(y=np.percentile(anomaly_scores, 95), color='r',
                    linestyle='--', label='95% Threshold')
        ax2.set_title('LOF Anomaly Scores')
        ax2.legend()

        plt.tight_layout()

        # 将图像转换为字节流
        img = BytesIO()
        plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        img.seek(0)

        # 将字节流转换为 Base64 字符串
        image_base64 = base64.b64encode(img.read()).decode('utf-8')

    return anomalies, image_base64


def modified_zscore_detection(series, threshold=3.5, show=False):
    """
    Modified Z-Score点异常检测
    使用中位数和MAD，对异常值更鲁棒
    """
    median = np.median(series)
    mad = np.median(np.abs(series - median))

    # 避免除零
    if mad == 0:
        mad = 1e-6

    modified_z_scores = 0.6745 * (series - median) / mad

    anomalies_mask = np.abs(modified_z_scores) > threshold
    anomalies = series[anomalies_mask]

    image_base64 = None
    if show:
        plt.figure(figsize=(12, 6))
        plt.plot(series.index, series.values,
                 'b-', alpha=0.7, label='raw data')
        plt.scatter(anomalies.index, anomalies.values, color='red',
                    s=80, label=f'Point Anomaly (Mod Z > {threshold})', zorder=5)
        plt.axhline(y=median + threshold * mad / 0.6745,
                    color='r', linestyle='--', alpha=0.5, label='Anomaly Threshold')
        plt.axhline(y=median - threshold * mad / 0.6745,
                    color='r', linestyle='--', alpha=0.5)
        plt.axhline(y=median, color='g', linestyle='-',
                    alpha=0.5, label='median')
        plt.title(f'Modified Z-Score  (threshold={threshold})')
        plt.legend()

        # 将图像转换为字节流
        img = BytesIO()
        plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        img.seek(0)

        # 将字节流转换为 Base64 字符串
        image_base64 = base64.b64encode(img.read()).decode('utf-8')

    return anomalies, image_base64


def elliptic_envelope_detection(X, contamination=0.1, show=False):
    """
    基于多元高斯分布的异常检测
    参数:
    X: pandas Series/dataframe，具有时间索引的数据
    contamination: 数据中异常值的比例
    show: 是否显示检测结果图像
    返回:
    anomalies: 检测到的异常点
    image_base64: Base64编码的图像字符串（show=True时）
    """
    # 输入验证
    if not isinstance(X, pd.Series):
        raise ValueError("X 必须是一个 pandas Series！")
    if len(X) < 2:
        raise ValueError("X 至少需要包含2个数据点！")
    # 检查 X 是否有时间索引，如果没有则使用默认索引
    if not isinstance(X.index, (pd.DatetimeIndex, pd.TimedeltaIndex)):
        print("警告: X 没有时间索引，将使用默认索引")
        # 创建默认的时间索引
        X = pd.Series(X.values, index=pd.date_range(
            '2024-01-01', periods=len(X), freq='H'))
    # 准备数据 - 确保是二维数组
    X_2d = X.values.reshape(-1, 1)
    # 使用椭圆包络检测异常
    envelope = EllipticEnvelope(
        contamination=contamination,
        random_state=42,
        support_fraction=0.8  # 添加支持分数以提高稳定性
    )
    try:
        labels = envelope.fit_predict(X_2d)
        anomalies = X[labels == -1]
        # 计算决策函数得分（异常分数）
        decision_scores = envelope.decision_function(X_2d)
    except Exception as e:
        # 如果拟合失败，回退到简单方法
        print(f"椭圆包络检测失败: {e}，使用Z-Score作为备选")
        return z_score_detection(X, show)

    image_base64 = None
    if show:
        plt.figure(figsize=(12, 8))
        # 子图1: 异常检测结果
        plt.subplot(2, 1, 1)
        plt.plot(X.index, X.values, 'b-', alpha=0.7,
                 label='Raw Data', linewidth=1)
        plt.scatter(anomalies.index, anomalies.values, color='red',
                    s=50, label=f'Outliers (contamination={contamination})', zorder=5)
        # Calculate and display Mahalanobis distance threshold
        threshold = np.percentile(decision_scores, contamination * 100)
        plt.title(
            f'Elliptic Envelope Outlier Detection (contamination: {contamination})')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True, alpha=0.3)
        # Subplot 2: Anomaly scores
        plt.subplot(2, 1, 2)
        plt.plot(X.index, decision_scores, 'g-',
                 alpha=0.7, label='Anomaly Scores')
        plt.axhline(y=threshold, color='r', linestyle='--',
                    label=f'Anomaly Threshold ({threshold:.3f})')
        plt.fill_between(X.index, decision_scores, threshold,
                         where=(decision_scores < threshold),
                         color='red', alpha=0.3, label='Anomaly Region')
        plt.ylabel('Anomaly Score')
        plt.xlabel('Time')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        # 将图像转换为字节流
        img = BytesIO()
        plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        img.seek(0)
        image_base64 = base64.b64encode(img.read()).decode('utf-8')
    return anomalies, image_base64


def show_base64(image_base64):
    """显示 Base64 编码的图像"""
    if image_base64 is None:
        return
    # 假设 image_base64 是你的 Base64 编码图像字符串
    image_data = base64.b64decode(image_base64)
    image = Image.open(BytesIO(image_data))
    # 将图像显示在 matplotlib 图像中
    plt.imshow(image)
    plt.axis('off')  # 隐藏坐标轴
    plt.show()


def check_gaussian_assumption(data, alpha=0.05, show=False):
    """检查数据是否近似高斯分布"""
    result = {}
    if isinstance(data, pd.DataFrame):
        for col in data.columns:
            report, image = _check_series_gaussian_assumption(data[col], alpha=alpha, show=show)
            result[col] = report['is_normal']
    elif isinstance(data, pd.Series):
        col = data.name
        report, image = _check_series_gaussian_assumption(data, alpha=alpha, show=show)
        result[col] = report['is_normal']
    return result, image

def _check_series_gaussian_assumption(series, alpha=0.05, show=False):
    """
    检查单列数据的高斯分布假设
    参数:
    data: pandas Series
    alpha: 显著性水平
    show: 是否显示分布图
    返回:
    result: 包含统计量和检验结果的字典
    """
    data = series.dropna()
    if len(data) < 3:
        print(f"警告: 列 '{series.name}' 数据点太少 ({len(data)})，跳过检验")
        return None
    # 基本统计量
    n = len(data)
    mean_val = np.mean(data)
    std_val = np.std(data)
    skewness = stats.skew(data)
    kurtosis = stats.kurtosis(data)
    # 多种正态性检验
    # 1. Shapiro-Wilk检验 (适合小样本)
    if n <= 5000:
        shapiro_stat, shapiro_p = shapiro(data)
    else:
        shapiro_stat, shapiro_p = shapiro(data.sample(5000, random_state=42))
    # 2. D'Agostino的K^2检验 (适合各种样本量)
    dagostino_stat, dagostino_p = stats.normaltest(data)
    # 3. Anderson-Darling检验
    anderson_stat = anderson(data, dist='norm')
    anderson_critical = anderson_stat.critical_values[2]  # 使用5%显著性水平
    anderson_reject = anderson_stat.statistic > anderson_critical
    # 4. Kolmogorov-Smirnov检验
    ks_stat, ks_p = kstest(data, 'norm', args=(mean_val, std_val))

    # 判断是否拒绝正态性假设
    reject_shapiro = shapiro_p < alpha if not np.isnan(
        shapiro_p) else np.nan
    reject_dagostino = dagostino_p < alpha
    reject_ks = ks_p < alpha

    # 综合判断 (多数检验拒绝则认为非正态)
    tests_rejected = sum(
        [reject_shapiro, reject_dagostino, reject_ks, anderson_reject])
    is_normal = tests_rejected >= 3  # 如果不超过1个检验拒绝，认为基本正态

    # 存储结果
    result = {
        'column': data.name,
        'n': n,
        'mean': mean_val,
        'std': std_val,
        'skewness': skewness,
        'kurtosis': kurtosis,
        'shapiro_p': shapiro_p,
        'dagostino_p': dagostino_p,
        'ks_p': ks_p,
        'anderson_stat': anderson_stat.statistic,
        'reject_shapiro': reject_shapiro,
        'reject_dagostino': reject_dagostino,
        'reject_ks': reject_ks,
        'reject_anderson': anderson_reject,
        'is_normal': is_normal,
        'normal_confidence': 'high' if tests_rejected == 0 else 'middle' if tests_rejected <= 1 else 'low'
    }
    # 可视化
    image_base64 = None
    if show:
        image_base64 = _plot_normality_check(data, data.name, result)
    return result, image_base64

def _plot_normality_check(data, col_name, result, figsize=(15, 4)):
    """Plot normality test charts"""
    plt.figure(figsize=(12, 8))
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    fig.suptitle(
        f'Normality Test - {col_name} (Normal: {result["is_normal"]})', fontsize=14)

    # 1. Histogram + Normal curve
    axes[0].hist(data, bins=30, density=True, alpha=0.7,
                 color='skyblue', edgecolor='black')

    # Add normal distribution curve
    xmin, xmax = axes[0].get_xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, result['mean'], result['std'])
    axes[0].plot(x, p, 'r-', linewidth=2, label='Normal Distribution')
    axes[0].set_title(
        f'Distribution Histogram\nSkewness: {result["skewness"]:.3f}, Kurtosis: {result["kurtosis"]:.3f}')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 2. Q-Q plot
    stats.probplot(data, dist="norm", plot=axes[1])
    axes[1].set_title('Q-Q Plot')
    axes[1].grid(True, alpha=0.3)

    # 3. Box plot
    axes[2].boxplot(data)
    axes[2].set_title('Box Plot')
    axes[2].set_ylabel('Value')
    axes[2].grid(True, alpha=0.3)

    # Add test results text
    text_str = f"""Test Results:
Shapiro-Wilk: p={result['shapiro_p']:.4f}
D'Agostino: p={result['dagostino_p']:.4f}
K-S: p={result['ks_p']:.4f}
Anderson: stat={result['anderson_stat']:.3f}
Normality: {result['is_normal']}
Confidence: {result['normal_confidence']}"""

    axes[2].text(1.1, 0.5, text_str, transform=axes[2].transAxes, verticalalignment='center',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    img = BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    img.seek(0)
    image_base64 = base64.b64encode(img.read()).decode('utf-8')
    return image_base64

def print_summary_report(results_df, alpha):
    """生成总结报告字符串"""
    report_lines = []
    report_lines.append("高斯分布假设检验总结报告")
    report_lines.append("=" * 80)
    normal_cols = results_df[results_df['is_normal']]['column'].tolist()
    non_normal_cols = results_df[~results_df['is_normal']]['column'].tolist()

    report_lines.append(f"# 数据概览:")
    report_lines.append(f"总列数: {len(results_df)}")
    report_lines.append(f"符合正态分布: {len(normal_cols)} 列")
    report_lines.append(f"不符合正态分布: {len(non_normal_cols)} 列")
    report_lines.append(f"显著性水平: α = {alpha}")

    if normal_cols:
        report_lines.append(f"\n 符合正态分布的列: {normal_cols}")

    if non_normal_cols:
        report_lines.append(f"\n 不符合正态分布的列: {non_normal_cols}")

    report_lines.append(f"\n 统计量范围:")
    report_lines.append(f"偏度范围: [{results_df['skewness'].min():.3f}, {results_df['skewness'].max():.3f}]")
    report_lines.append(f"峰度范围: [{results_df['kurtosis'].min():.3f}, {results_df['kurtosis'].max():.3f}]")

    # 正态性建议
    report_lines.append(f"\n 建议:")
    normal_ratio = len(normal_cols) / len(results_df)
    if normal_ratio >= 0.8:
        report_lines.append("大部分数据符合正态分布，适合使用基于高斯假设的算法")
    elif normal_ratio >= 0.5:
        report_lines.append("约一半数据符合正态分布，可考虑数据变换或使用鲁棒算法")
    else:
        report_lines.append("大部分数据不符合正态分布，建议使用非参数方法")
    # 返回完整的报告字符串
    return "\n".join(report_lines)


def remove_duplicates(ts_data):
    """处理重复的时间戳"""
    # 方法1: 删除完全重复的行
    ts_cleaned = ts_data.drop_duplicates()
    
    # 方法2: 基于时间戳去重，保留最后一个
    ts_cleaned = ts_data[~ts_data.index.duplicated(keep='last')]
    
    # 方法3: 对重复时间戳的值进行聚合
    ts_cleaned = ts_data.groupby(ts_data.index).mean()
    
    return ts_cleaned


if __name__ == "__main__":
    # 示例用法
    df = read_data("/mnt/d/rainpy/tests/test_data/ETTh1.csv")
    result, image = check_gaussian_assumption(df, alpha=0.05, show=True)
    show_base64(image)
    print(result)