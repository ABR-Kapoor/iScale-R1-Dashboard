import pandas as pd

class iScaleAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        
    def load_and_process_data(self):
        try:
            self.df = pd.read_csv(self.file_path, low_memory=False)
            datetime_cols = ['handled_time', 'slot_start_time', 'payment_time']
            for col in datetime_cols:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            
            self.df['conversion_flag'] = (~self.df['payment_time'].isna()).astype(int)
            self.df['connectivity_flag'] = (self.df['booked_flag'] == 'Booked').astype(int)
            self.df['slot_hour'] = self.df['slot_start_time'].dt.hour
            self.df['conversion_days'] = (self.df['payment_time'] - self.df['slot_start_time']).dt.days
            self.df['lead_type'] = self.df['India vs NRI'] + '_' + self.df['medicalconditionflag'].map({
                True: 'Medical', False: 'NonMedical', 'Yes': 'Medical', 'No': 'NonMedical'
            })
            return True
        except:
            return False
    
    def get_basic_metrics(self):
        if self.df is None: return None
        return {
            'total_consultations': len(self.df),
            'total_conversions': self.df['conversion_flag'].sum(),
            'overall_conversion_rate': (self.df['conversion_flag'].sum() / len(self.df) * 100),
            'active_coaches': self.df['expert_id'].nunique(),
            'unique_funnels': self.df['funnel'].nunique(),
            'unique_lead_types': self.df['lead_type'].nunique()
        }
    
    def calculate_conversion_rates(self, days):
        if self.df is None: return None
        conversion_mask = (self.df['conversion_days'] <= days) & (self.df['conversion_days'] >= 0)
        
        conversion_stats = self.df.groupby(['funnel', 'lead_type']).agg({
            'user_id': 'count', 'conversion_flag': 'sum'
        }).reset_index()
        
        conversion_within_days = self.df[conversion_mask].groupby(['funnel', 'lead_type']).agg({
            'conversion_flag': 'sum'
        }).reset_index()
        conversion_within_days.rename(columns={'conversion_flag': f'conversions_{days}d'}, inplace=True)
        
        result = conversion_stats.merge(conversion_within_days, on=['funnel', 'lead_type'], how='left')
        result[f'conversions_{days}d'] = result[f'conversions_{days}d'].fillna(0)
        result[f'conversion_rate_{days}d'] = (result[f'conversions_{days}d'] / result['user_id'] * 100).round(2)
        
        return result
    
    def analyze_hourly_performance(self):
        if self.df is None: return None
        hourly_stats = self.df.groupby('slot_hour').agg({
            'user_id': 'count',
            'connectivity_flag': 'sum',
            'conversion_flag': 'sum'
        }).reset_index()
        hourly_stats['connectivity_rate'] = (hourly_stats['connectivity_flag'] / hourly_stats['user_id'] * 100).round(2)
        hourly_stats['conversion_rate'] = (hourly_stats['conversion_flag'] / hourly_stats['user_id'] * 100).round(2)
        return hourly_stats
    
    def analyze_coach_performance(self):
        if self.df is None: return None
        coach_stats = self.df.groupby(['expert_id', 'target_class']).agg({
            'user_id': 'count',
            'conversion_flag': 'sum'
        }).reset_index()
        coach_stats['conversion_rate'] = (coach_stats['conversion_flag'] / coach_stats['user_id'] * 100).round(2)
        coach_stats['coach_name'] = 'Coach_' + coach_stats['expert_id'].astype(str)
        
        coach_class_stats = self.df.groupby('target_class').agg({
            'user_id': 'count',
            'conversion_flag': 'sum'
        }).reset_index()
        coach_class_stats['conversion_rate'] = (coach_class_stats['conversion_flag'] / coach_class_stats['user_id'] * 100).round(2)
        coach_class_stats = coach_class_stats.sort_values('conversion_rate', ascending=False)
        
        return {
            'individual_coaches': coach_stats,
            'class_performance': coach_class_stats
        }
    
    def analyze_funnel_performance(self):
        if self.df is None: return None
        funnel_stats = self.df.groupby('funnel').agg({
            'user_id': 'count',
            'conversion_flag': 'sum'
        }).reset_index()
        funnel_stats['conversion_rate'] = (funnel_stats['conversion_flag'] / funnel_stats['user_id'] * 100).round(2)
        return funnel_stats.sort_values('conversion_rate', ascending=False)
    
    def get_distribution_data(self):
        if self.df is None: return None
        return self.df[['funnel', 'lead_type', 'target_class', 'slot_hour', 'conversion_flag']].copy()
    
    def generate_key_insights(self):
        if self.df is None: return None
        
        hourly_stats = self.analyze_hourly_performance()
        coach_analysis = self.analyze_coach_performance()
        funnel_analysis = self.analyze_funnel_performance()
        
        best_hour = hourly_stats.loc[hourly_stats['conversion_rate'].idxmax()]
        top_hours = hourly_stats.nlargest(3, 'conversion_rate')
        peak_hours = top_hours['slot_hour'].tolist()
        
        best_coach_class = coach_analysis['class_performance'].iloc[0]
        worst_coach_class = coach_analysis['class_performance'].iloc[-1]
        
        best_funnel = funnel_analysis.iloc[0]
        worst_funnel = funnel_analysis.iloc[-1]
        
        return {
            'timing': {
                'best_conversion_hour': int(best_hour['slot_hour']),
                'avg_conversion_peak': best_hour['conversion_rate'],
                'peak_hours': peak_hours
            },
            'coach': {
                'best_class': best_coach_class['target_class'],
                'best_class_rate': best_coach_class['conversion_rate'],
                'worst_class_rate': worst_coach_class['conversion_rate'],
                'performance_gap': best_coach_class['conversion_rate'] - worst_coach_class['conversion_rate']
            },
            'funnel': {
                'best_funnel': best_funnel['funnel'],
                'best_funnel_rate': best_funnel['conversion_rate'],
                'worst_funnel': worst_funnel['funnel'],
                'worst_funnel_rate': worst_funnel['conversion_rate'],
                'performance_gap': best_funnel['conversion_rate'] - worst_funnel['conversion_rate']
            },
            'overall': {
                'total_consultations': len(self.df),
                'overall_conversion_rate': (self.df['conversion_flag'].mean() * 100)
            }
        }
    
    def generate_actionable_recommendations(self):
        insights = self.generate_key_insights()
        if not insights: return None
        
        current_rate = insights['overall']['overall_conversion_rate']
        potential_improvement = (insights['coach']['performance_gap'] * 0.3) + (insights['funnel']['performance_gap'] * 0.2)
        potential_rate = current_rate + potential_improvement
        
        monthly_consultations = len(self.df) * 4
        additional_conversions = int((potential_rate - current_rate) / 100 * monthly_consultations)
        
        return {
            'immediate': [
                f"Focus 70% of slots during peak hours: {', '.join(map(str, insights['timing']['peak_hours']))}",
                f"Prioritize Class {insights['coach']['best_class']} coaches for high-value leads",
                f"Scale {insights['funnel']['best_funnel']} funnel marketing budget"
            ],
            'short_term': [
                f"Train lower-tier coaches using Class {insights['coach']['best_class']} best practices",
                f"Optimize {insights['funnel']['worst_funnel']} funnel conversion process",
                "Implement dynamic coach-lead matching based on lead value"
            ],
            'potential_impact': {
                'current_conversion_rate': round(current_rate, 1),
                'potential_conversion_rate': round(potential_rate, 1),
                'improvement_percentage': round(potential_improvement, 1),
                'additional_conversions_monthly': additional_conversions
            }
        }

def export_analysis_results(analyzer, output_path="analysis_results.json"):
    if analyzer.df is None: return False
    
    results = {
        'basic_metrics': analyzer.get_basic_metrics(),
        'conversion_3d': analyzer.calculate_conversion_rates(3).to_dict('records'),
        'conversion_7d': analyzer.calculate_conversion_rates(7).to_dict('records'),
        'hourly_performance': analyzer.analyze_hourly_performance().to_dict('records'),
        'coach_performance': analyzer.analyze_coach_performance(),
        'funnel_performance': analyzer.analyze_funnel_performance().to_dict('records'),
        'key_insights': analyzer.generate_key_insights(),
        'recommendations': analyzer.generate_actionable_recommendations()
    }
    
    import json
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    return True

def create_summary_report(analyzer):
    insights = analyzer.generate_key_insights()
    recommendations = analyzer.generate_actionable_recommendations()
    
    return f"""iScale Analytics Report
Total: {insights['overall']['total_consultations']:,} consultations
Conversion: {insights['overall']['overall_conversion_rate']:.1f}%
Best Funnel: {insights['funnel']['best_funnel']} ({insights['funnel']['best_funnel_rate']:.1f}%)
Peak Hours: {', '.join(map(str, insights['timing']['peak_hours']))}
Top Coach Class: {insights['coach']['best_class']} ({insights['coach']['best_class_rate']:.1f}%)
Potential Improvement: +{recommendations['potential_impact']['improvement_percentage']:.1f}%"""

if __name__ == "__main__":
    file_path = r'e:\py\iScale-round1\iScale_MaskedData.csv'
    analyzer = iScaleAnalyzer(file_path)
    if analyzer.load_and_process_data():
        insights = analyzer.generate_key_insights()
        recommendations = analyzer.generate_actionable_recommendations()
        export_analysis_results(analyzer)
    else:
        print("Error loading data.")