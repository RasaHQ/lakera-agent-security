import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MockLoanQualificationAPI:
    """
    A mock loan qualification API that determines loan approval and terms
    based on customer profile and requested vehicle price.
    """

    def __init__(self):
        # Interest rate matrix based on credit score tiers
        self.rate_matrix = {
            "excellent": {"min_score": 750, "base_rate": 3.2},  # 750+
            "good": {"min_score": 700, "base_rate": 4.1},       # 700-749  
            "fair": {"min_score": 650, "base_rate": 6.8},       # 650-699
            "subprime": {"min_score": 0, "base_rate": 12.5}     # <650
        }
        
        # Available loan terms (months)
        self.available_terms = [36, 48, 60, 72]

    def _get_credit_tier(self, credit_score: int) -> str:
        """Determine credit tier based on score"""
        if credit_score >= 750:
            return "excellent"
        elif credit_score >= 700:
            return "good" 
        elif credit_score >= 650:
            return "fair"
        else:
            return "subprime"

    def _calculate_monthly_payment(self, principal: float, annual_rate: float, term_months: int) -> float:
        """Calculate monthly payment using standard loan formula"""
        if term_months <= 0:
            return 0.0
            
        monthly_rate = annual_rate / 12 / 100
        
        if monthly_rate == 0:
            return principal / term_months
        
        numerator = monthly_rate * (1 + monthly_rate) ** term_months
        denominator = (1 + monthly_rate) ** term_months - 1
        
        return principal * (numerator / denominator)

    def check_loan_qualification(
        self, 
        vehicle_price: float,
        customer_profile: dict,
        down_payment: Optional[float] = None
    ) -> str:
        """
        Check loan qualification based on vehicle price and customer profile.
        
        Args:
            vehicle_price (float): Price of the vehicle
            customer_profile (dict): Customer financial data
            down_payment (float, optional): Down payment amount
            
        Returns:
            str: JSON string with qualification results
        """
        logger.debug(f"check_loan_qualification called")
        logger.debug(f"vehicle_price=${vehicle_price}, down_payment=${down_payment}")
        logger.debug(f"customer credit_score={customer_profile.get('credit_score')}")
        
        try:
            # Extract customer data
            credit_score = customer_profile["credit_score"]
            annual_income = customer_profile["annual_income"]
            monthly_debt = customer_profile["monthly_debt_payments"]
            account_balance = customer_profile["account_balance"]
            
            # Calculate loan amount
            loan_amount = vehicle_price
            if down_payment:
                loan_amount = vehicle_price - down_payment
            
            # Get credit tier and base rate  
            credit_tier = self._get_credit_tier(credit_score)
            base_rate = self.rate_matrix[credit_tier]["base_rate"]
            
            # Calculate debt-to-income ratios for different terms
            monthly_income = annual_income / 12
            current_dti = monthly_debt / monthly_income
            
            response = {
                "approved": False,
                "vehicle_price": vehicle_price,
                "loan_amount": loan_amount,
                "down_payment": down_payment or 0,
                "credit_tier": credit_tier,
                "credit_score": credit_score,
                "current_debt_to_income": round(current_dti, 3),
                "loan_options": [],
                "denial_reason": None
            }
            
            # Check maximum loan amount (typically 35-40% of annual income)
            max_loan_amount = annual_income * 0.38
            if loan_amount > max_loan_amount:
                response["denial_reason"] = f"Requested loan amount (${loan_amount:,.0f}) exceeds maximum based on income (${max_loan_amount:,.0f})"
                return json.dumps(response)
            
            # Calculate options for different terms
            approved_options = []
            
            for term in self.available_terms:
                monthly_payment = self._calculate_monthly_payment(loan_amount, base_rate, term)
                new_dti = (monthly_debt + monthly_payment) / monthly_income
                
                # Check if DTI is acceptable (typically under 40%)
                if new_dti <= 0.40:
                    total_interest = (monthly_payment * term) - loan_amount
                    
                    approved_options.append({
                        "term_months": term,
                        "monthly_payment": round(monthly_payment, 2),
                        "interest_rate": base_rate,
                        "total_interest": round(total_interest, 2),
                        "new_debt_to_income": round(new_dti, 3)
                    })
            
            if approved_options:
                response["approved"] = True
                response["loan_options"] = approved_options
                
                # Suggest down payment if beneficial
                if not down_payment and account_balance > 5000:
                    suggested_down = min(account_balance * 0.5, vehicle_price * 0.2)
                    response["suggested_down_payment"] = round(suggested_down, 0)
            else:
                response["denial_reason"] = "Debt-to-income ratio too high for available loan terms"
            
            return json.dumps(response)
            
        except KeyError as e:
            return json.dumps({
                "error": f"Missing required customer data: {e}",
                "approved": False
            })
        except Exception as e:
            return json.dumps({
                "error": f"Qualification check failed: {str(e)}",
                "approved": False
            })


# Example usage for testing
if __name__ == "__main__":
    qualification_api = MockLoanQualificationAPI()
    
    # Test customer profile
    customer_profile = {
        "customer_id": "CUST_12345",
        "credit_score": 720,
        "annual_income": 85000,
        "monthly_debt_payments": 1200,
        "account_balance": 15000
    }
    
    # Test 1: Good customer, reasonable car price
    print("--- Test 1: $28,000 car, good customer ---")
    result1 = qualification_api.check_loan_qualification(28000, customer_profile)
    print(json.dumps(json.loads(result1), indent=2))
    
    # Test 2: Same customer with down payment
    print("\n--- Test 2: $28,000 car with $5,000 down ---")
    result2 = qualification_api.check_loan_qualification(28000, customer_profile, 5000)
    print(json.dumps(json.loads(result2), indent=2))
    
    # Test 3: Expensive car (should be denied)
    print("\n--- Test 3: $60,000 car (too expensive) ---")
    result3 = qualification_api.check_loan_qualification(60000, customer_profile)
    print(json.dumps(json.loads(result3), indent=2))
    
    # Test 4: Lower credit score customer
    low_credit_customer = {
        "customer_id": "CUST_67890",
        "credit_score": 680,
        "annual_income": 65000, 
        "monthly_debt_payments": 800,
        "account_balance": 8000
    }
    
    print("\n--- Test 4: Lower credit customer ---")
    result4 = qualification_api.check_loan_qualification(25000, low_credit_customer)
    print(json.dumps(json.loads(result4), indent=2))