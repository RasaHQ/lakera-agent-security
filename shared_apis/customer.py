import json
import random


class MockCustomerAPI:
    """
    A mock customer API that simulates a bank's internal customer data system.
    Returns customer financial profile for loan qualification.
    """

    def __init__(self):
        # Mock customer database - in reality this would come from bank systems
        self.customers = {
            "CUST_12345": {
                "customer_id": "CUST_12345",
                "credit_score": 720,
                "annual_income": 85000,
                "monthly_debt_payments": 1200,
                "account_balance": 15000
            },
            "CUST_67890": {
                "customer_id": "CUST_67890", 
                "credit_score": 680,
                "annual_income": 65000,
                "monthly_debt_payments": 800,
                "account_balance": 8000
            },
            "CUST_11111": {
                "customer_id": "CUST_11111",
                "credit_score": 760,
                "annual_income": 95000,
                "monthly_debt_payments": 1500,
                "account_balance": 25000
            }
        }

    def get_customer_profile(self, customer_id: str = None):
        """
        Get customer financial profile for loan qualification.
        
        Args:
            customer_id (str): Customer ID. If None, returns default customer.
            
        Returns:
            str: JSON string with customer financial data
        """
        print(f"DEBUG (MockCustomerAPI): get_customer_profile called with customer_id='{customer_id}'")
        
        # If no customer_id provided, use a default one (simulates logged-in user)
        if not customer_id:
            customer_id = "CUST_12345"
        
        customer_data = self.customers.get(customer_id)
        
        if not customer_data:
            return json.dumps({
                "error": f"Customer {customer_id} not found"
            })
        
        print(f"DEBUG (MockCustomerAPI): Found customer with credit_score={customer_data['credit_score']}, income=${customer_data['annual_income']}")
        
        return json.dumps(customer_data)


# Example usage for testing
if __name__ == "__main__":
    customer_api = MockCustomerAPI()
    
    # Test default customer
    result1 = customer_api.get_customer_profile()
    print("--- Default Customer ---")
    print(json.dumps(json.loads(result1), indent=2))
    
    # Test specific customer
    result2 = customer_api.get_customer_profile("CUST_67890")
    print("\n--- Customer 67890 ---")
    print(json.dumps(json.loads(result2), indent=2))
    
    # Test non-existent customer
    result3 = customer_api.get_customer_profile("CUST_99999")
    print("\n--- Non-existent Customer ---")
    print(json.dumps(json.loads(result3), indent=2))