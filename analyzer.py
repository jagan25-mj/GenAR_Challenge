import pandas as pd
import os

class DataAnalyzer:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = pd.read_excel(data_path)
        
        # Clean up column names just in case
        self.df.columns = self.df.columns.str.strip().str.lower()
        
        # Determine reporting period from receivedate
        if 'receivedate' in self.df.columns:
            self.df['receivedate'] = pd.to_datetime(self.df['receivedate'], errors='coerce')
            self.min_date = self.df['receivedate'].min()
            self.max_date = self.df['receivedate'].max()
        else:
            self.min_date = None
            self.max_date = None

        # Data prep: serious vs non-serious
        # Almost every case is flagged serious (1023 of 1024)
        if 'serious' in self.df.columns:
            self.df['is_serious'] = self.df['serious'].astype(str).str.lower() == 'serious'
        else:
            # Fallback if specific flag is missing
            self.df['is_serious'] = False

        # Create age buckets
        if 'patient_patientonsetage' in self.df.columns:
            self.df['patient_patientonsetage'] = pd.to_numeric(self.df['patient_patientonsetage'], errors='coerce')
            bins = [0, 17, 64, 120]
            labels = ['0-17', '18-64', '65+']
            self.df['age_group_derived'] = pd.cut(self.df['patient_patientonsetage'], bins=bins, labels=labels)

        # Create a deduped dataframe for case-level metrics
        self.df_cases = self.df.drop_duplicates(subset=['safetyreportid'])

    def get_reporting_period(self) -> dict:
        if pd.notnull(self.min_date) and pd.notnull(self.max_date):
            return {
                "start_date": self.min_date.strftime('%B %d, %Y'),
                "end_date": self.max_date.strftime('%B %d, %Y')
            }
        return {"start_date": "Unknown", "end_date": "Unknown"}

    def get_case_volume(self) -> dict:
        total_cases = len(self.df_cases)
        serious_cases = self.df_cases['is_serious'].sum()
        non_serious_cases = total_cases - serious_cases
        
        return {
            "total_cases": int(total_cases),
            "serious_cases": int(serious_cases),
            "non_serious_cases": int(non_serious_cases)
        }

    def get_demographics(self) -> dict:
        # Age
        age_counts = {}
        if 'age_group_derived' in self.df_cases.columns:
            age_counts = self.df_cases['age_group_derived'].value_counts(dropna=False).to_dict()
        
        # Sex
        sex_counts = {}
        if 'patient_patientsex' in self.df_cases.columns:
            sex_counts = self.df_cases['patient_patientsex'].value_counts(dropna=False).to_dict()

        # Country
        country_counts = {}
        if 'occurcountry' in self.df_cases.columns:
            country_counts = self.df_cases['occurcountry'].value_counts().head(5).to_dict()
            
        return {
            "age_groups": age_counts,
            "sex": sex_counts,
            "top_countries": country_counts
        }

    def get_reactions(self, top_n: int = 10) -> dict:
        # Reaction level metrics (not deduped by case)
        if 'patient_reaction_reactionmeddrapt' not in self.df.columns:
            return {}

        top_reactions = self.df['patient_reaction_reactionmeddrapt'].value_counts().head(top_n).to_dict()
        
        # Serious reactions
        serious_df = self.df[self.df['is_serious'] == True]
        top_serious_reactions = serious_df['patient_reaction_reactionmeddrapt'].value_counts().head(top_n).to_dict()

        return {
            "top_reactions": top_reactions,
            "top_serious_reactions": top_serious_reactions
        }

    def get_outcomes(self) -> dict:
        # Outcome is often at the reaction level
        if 'patient_reaction_reactionoutcome' not in self.df.columns:
            return {}
        outcomes = self.df['patient_reaction_reactionoutcome'].value_counts().to_dict()
        return {"outcomes": outcomes}

    def get_serious_criteria(self) -> dict:
        criteria_cols = [
            'seriousnessdeath', 'seriousnesslifethreatening',
            'seriousnesshospitalization', 'seriousnessdisabling',
            'seriousnesscongenitalanomali', 'seriousnessother'
        ]
        results = {}
        for col in criteria_cols:
            if col in self.df_cases.columns:
                count = (self.df_cases[col].astype(str).str.lower() == 'yes').sum()
                results[col] = int(count)
        return results

if __name__ == "__main__":
    # Test execution
    test_path = "../Bisoprolol_icsr_sample_1068rows.xlsx"
    if os.path.exists(test_path):
        analyzer = DataAnalyzer(test_path)
        print("Reporting Period:", analyzer.get_reporting_period())
        print("Case Volume:", analyzer.get_case_volume())
        print("Reactions:", analyzer.get_reactions(3))
    else:
        print(f"Test data not found at {test_path}")
