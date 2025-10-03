"""
Invoice Agent for workspace-specific invoice management
"""

from typing import Dict, Any, List, Optional

try:
    from apps.agents.figents.v1.base import BaseWorkspaceAgent
except ImportError:
    BaseWorkspaceAgent = None


class InvoiceAgent(BaseWorkspaceAgent):
    """Invoice Agent for handling invoice-related tasks"""

    def __init__(self, workspace_id: str, llm_provider: str = "gemini"):
        super().__init__(workspace_id, "Invoice Agent", llm_provider)

    @property
    def role(self) -> str:
        """Role of the Invoice Agent"""
        return f"Invoice Management Specialist for workspace {self.workspace_id}"

    @property
    def goal(self) -> str:
        """Goal of the Invoice Agent"""
        return (
            "Manage invoices efficiently by creating, processing, analyzing, "
            "and providing insights on invoice data for the workspace"
        )

    @property
    def backstory(self) -> str:
        """Backstory of the Invoice Agent"""
        return (
            f"You are an expert invoice management specialist for workspace {self.workspace_id}. "
            "You have extensive experience in financial document processing, invoice analysis, "
            "and billing systems. You can create professional invoices, analyze payment patterns, "
            "identify discrepancies, and provide financial insights. You're detail-oriented and "
            "ensure accuracy in all financial operations."
        )

    @property
    def tools(self) -> list:
        """Tools of the Invoice Agent"""
        return [
            # Add specific tools for invoice operations here,
            # for example, PDF generation, data extraction libraries, etc.
        ]

    def create_invoice(self, invoice_data: Dict[str, Any]) -> str:
        """Create a new invoice based on provided data"""
        task_description = f"""
        Create a professional invoice with the following data:

        Invoice Data: {invoice_data}
        Workspace: {self.workspace_id}

        Generate a complete invoice that includes:
        - Professional header with workspace branding
        - Detailed line items with descriptions and amounts
        - Tax calculations
        - Payment terms and due date
        - Contact information
        - Unique invoice number
        """

        expected_output = """
        A complete, professional invoice document that includes:
        1. Proper invoice formatting and structure
        2. All required financial details
        3. Clear payment instructions
        4. Professional presentation
        5. Compliance with standard invoice practices
        """

        return self.execute_task(task_description, expected_output)

    def analyze_invoice_data(self, invoice_data: List[Dict[str, Any]]) -> str:
        """Analyze invoice data and provide insights"""
        task_description = f"""
        Analyze the following invoice data for workspace {self.workspace_id}:

        Invoice Data: {invoice_data}

        Provide comprehensive analysis including:
        - Revenue trends and patterns
        - Payment status analysis
        - Outstanding amounts
        - Customer payment behavior
        - Recommendations for improvement
        - Risk assessment
        """

        expected_output = """
        A detailed financial analysis report that includes:
        1. Revenue and payment trend analysis
        2. Outstanding payment identification
        3. Customer payment behavior insights
        4. Risk assessment and recommendations
        5. Actionable improvement suggestions
        """

        return self.execute_task(task_description, expected_output)

    def process_payment(self, payment_data: Dict[str, Any]) -> str:
        """Process a payment for an invoice"""
        task_description = f"""
        Process this payment for workspace {self.workspace_id}:

        Payment Data: {payment_data}

        Handle the payment processing by:
        - Verifying payment details
        - Updating invoice status
        - Recording payment information
        - Generating payment confirmation
        - Updating customer records
        """

        expected_output = """
        Payment processing confirmation that includes:
        1. Payment verification details
        2. Updated invoice status
        3. Payment confirmation number
        4. Updated customer account information
        5. Next steps or follow-up actions
        """

        return self.execute_task(task_description, expected_output)

    def generate_invoice_report(
        self, date_range: Dict[str, str], report_type: str = "summary"
    ) -> str:
        """Generate invoice reports for the workspace"""
        task_description = f"""
        Generate a {report_type} invoice report for workspace {self.workspace_id}:

        Date Range: {date_range}
        Report Type: {report_type}

        Create a comprehensive report including:
        - Invoice summary statistics
        - Revenue analysis
        - Payment status breakdown
        - Outstanding amounts
        - Customer analysis
        - Recommendations
        """

        expected_output = """
        A professional invoice report that includes:
        1. Executive summary
        2. Detailed financial metrics
        3. Visual data representation (if applicable)
        4. Key insights and trends
        5. Actionable recommendations
        6. Appendices with detailed data
        """

        return self.execute_task(task_description, expected_output)

    def handle_invoice_query(
        self, query: str, invoice_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Handle general invoice-related queries"""
        context = self.get_workspace_context()
        if invoice_context:
            context.update(invoice_context)

        task_description = f"""
        Handle this invoice-related query: "{query}"

        Context:
        - Workspace: {self.workspace_id}
        - Invoice context: {invoice_context or 'No additional context'}

        Provide a comprehensive response that addresses the query with:
        - Clear explanation of invoice concepts
        - Step-by-step guidance if needed
        - Relevant examples
        - Next steps for the user
        """

        expected_output = """
        A helpful response that:
        1. Directly addresses the query
        2. Provides clear explanations
        3. Includes practical examples
        4. Offers actionable next steps
        5. Maintains professional tone
        """

        return self.execute_task(task_description, expected_output)
