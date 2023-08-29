from pydantic import BaseModel, Field
from db import DynamoDBClient


class CreditInfo(BaseModel):
    link: str = Field(alias='link')
    terms: str = Field(alias='terms')


class Credit(BaseModel):
    credit_info: CreditInfo = Field(alias='credit_info')
    name: str = Field(alias='credit_name')


class ATM(BaseModel):
    name: str = Field(alias='name')


class Card(BaseModel):
    info: str = Field(alias='card_info')
    name: str = Field(alias='card_name')


class DepositInfo(BaseModel):
    link: str = Field(alias='link')
    terms: str = Field(alias='deposit_terms')


class Deposit(BaseModel):
    deposit_info: DepositInfo = Field(alias='deposit_info')
    name: str = Field(alias='deposit_name')


class ExchangeRate(BaseModel):
    name: str = Field(alias='currency_name')
    sell: str = Field(alias='sell')
    buy: str = Field(alias='buy')


class InsuranceInfo(BaseModel):
    link: str = Field(alias='link')
    terms: str = Field(alias='terms')


class Insurance(BaseModel):
    insurance_info: InsuranceInfo = Field(alias='insurance_info')
    name: str = Field(alias='insurance_name')


class MoneyTransferInfo(BaseModel):
    link: str = Field(alias='description')
    name: str = Field(alias='name')


class BankAccountInfo(BaseModel):
    link: str = Field(alias='link')
    terms: str = Field(alias='terms')


class BankAccount(BaseModel):
    bank_account_info: BankAccountInfo = Field(alias='info')
    name: str = Field(alias='name')
