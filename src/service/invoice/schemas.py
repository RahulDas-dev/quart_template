from pydantic import BaseModel, Field, PositiveInt


class Item(BaseModel):
    """
    Structured model for summarizing item details in the invoice.
    """

    slno: PositiveInt
    description: str = Field(default="NOT_AVAILABLE", description="Description of the item")
    quantity: str = Field(default="NOT_AVAILABLE", description="Quantity of the item")
    price: str = Field(default="NOT_AVAILABLE", description="Price of the item")
    currency: str = Field(default="INR", description="Currency of the price")

    @property
    def is_empty(self) -> bool:
        return (
            self.description == "NOT_AVAILABLE" and self.quantity == "NOT_AVAILABLE" and self.price == "NOT_AVAILABLE"
        )


class CompanyDetails(BaseModel):
    """
    Structured model for summarizing company details.
    """

    name: str = Field(default="NOT_AVAILABLE", description="Name of the company")
    gst_no: str = Field(default="NOT_AVAILABLE", description="GST No of the company")
    pan_no: str = Field(default="NOT_AVAILABLE", description="PAN No of the company")
    address: str = Field(default="NOT_AVAILABLE", description="Address of the company")
    phone_number: str = Field(default="NOT_AVAILABLE", description="Phone number of the company")
    email: str = Field(default="NOT_AVAILABLE", description="Email of the company")

    @property
    def is_empty(self) -> bool:
        return (
            self.name == "NOT_AVAILABLE"
            and self.gst_no == "NOT_AVAILABLE"
            and self.pan_no == "NOT_AVAILABLE"
            and self.address == "NOT_AVAILABLE"
            and self.phone_number == "NOT_AVAILABLE"
            and self.email == "NOT_AVAILABLE"
        )


class TaxComponents(BaseModel):
    """
    Structured model for summarizing tax components.
    """

    CGST: float = Field(default=0.0, description="Central Goods and Services Tax")
    SGST: float = Field(default=0.0, description="State Goods and Services Tax")
    IGST: float = Field(default=0.0, description="Integrated Goods and Services Tax")

    @property
    def is_empty(self) -> bool:
        return self.CGST == 0.0 and self.SGST == 0.0 and self.IGST == 0.0


class Invoice(BaseModel):
    """
    Structured model for summarizing invoice details.
    """

    invoice_number: str = Field(default="NOT_AVAILABLE", description="Invoice number")
    invoice_date: str = Field(default="NOT_AVAILABLE", description="Invoice date")
    seller_details: CompanyDetails = Field(
        default_factory=lambda: CompanyDetails(), description="Details of the seller Comapny"
    )
    buyer_details: CompanyDetails = Field(
        default_factory=lambda: CompanyDetails(), description="Details of the buyer Company"
    )
    items: list[Item] = Field(default_factory=list, description="List of items in the invoice")
    total_tax: TaxComponents = Field(default_factory=lambda: TaxComponents(), description="Total tax components")
    total_charge: float = Field(default=0.0, description="Total charges")
    total_discount: float = Field(default=0.0, description="Total discount applied")
    total_amount: float = Field(default=0.0, description="Total amount of the invoice")
    amount_paid: float = Field(default=0.0, description="Amount paid")
    amount_due: float = Field(default=0.0, description="Amount due")
    page_no: int = Field(default=0, description="Page no , Where the Information Available")

    @property
    def is_empty(self) -> bool:
        return (
            self.invoice_number == "NOT_AVAILABLE"
            and self.invoice_date == "NOT_AVAILABLE"
            and self.buyer_details.is_empty
            and self.seller_details.is_empty
            and (all(item.is_empty for item in self.items) or not self.items)
            and self.total_tax.is_empty
            and self.total_charge == 0.0
            and self.total_discount == 0.0
            and self.total_amount == 0.0
            and self.amount_paid == 0.0
            and self.amount_due == 0.0
        )


class InvoiceData(BaseModel):
    """Structured model for summarizing invoice details from List of pages."""

    details: list[Invoice] = Field(description="Deatils of invoice present per page", default_factory=list)
