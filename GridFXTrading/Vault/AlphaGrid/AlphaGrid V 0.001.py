
#property copyright "Alpha Grid LTD"
#property version   "0.001"



extern double gLotSize = 0.1; // Set the lot size of the order
extern double gMaxSlippage = 10; // Maximum slippage allowed while opening the trade
extern double gTakeProfit = 100; // Set the take profit in points
extern double gStopLoss = 10000; // Set the stop loss in points
extern double gMagicNumber = 123; // Magic number for opening the trade
extern string gOrderSendComment = "AlphaGrid V 0.001" ; // Order Comment 
extern int gMaxOrders = 18; // Maximum allowed Open Order
extern double gDrawdown = 1; // allowed drawdown in percentage !!

// Assigning variable names 

int BuyOrderInfoArray[100][2];
int SellOrderInfoArray[100][2];
int OrderCount;

class CTrade {
private:
    double lotSize;
    double maxSlippage;
    double takeProfit;
    double stopLoss;
    int magicNumber;
    string orderSendComment;

public:
    CTrade(double lotSize, double maxSlippage, double takeProfit, double stopLoss, int magicNumber, string orderSendComment) {
        this.lotSize = lotSize;
        this.maxSlippage = maxSlippage;
        this.takeProfit = takeProfit;
        this.stopLoss = stopLoss;
        this.magicNumber = magicNumber;
        this.orderSendComment = orderSendComment;
    }

    int BuyNow() 
    {
        double takeProfit = Ask + this.takeProfit * Point; // Set the take profit gTakeProfit points above the Ask price
        double stopLoss = Bid - this.stopLoss * Point; // Set the stop loss gStopLoss below Bid price

        // Open a buy order with the specified lot size, entry price, and take profit
        int ticket = OrderSend(Symbol(), OP_BUY, this.lotSize, Ask, this.maxSlippage, stopLoss, takeProfit, this.orderSendComment, this.magicNumber, 0, Blue);

        if (ticket > 0) {
            Print("Buy order opened successfully with ticket #", ticket);
            return ticket;
        } else {
            Print("Failed to open buy order with error code #", GetLastError());
            return 0;
        }
    }

    int SellNow() 
    {
        double takeProfit = Bid - this.takeProfit * Point; // Set the take profit TakeProfit points below the Bid price
        double stopLoss = Ask + this.stopLoss * Point; // Set the stop loss gStopLoss above Bid price

        // Open a sell order with the specified lot size, entry price, take profit, and stop loss
        int ticket = OrderSend(Symbol(), OP_SELL, this.lotSize, Bid, this.maxSlippage, stopLoss, takeProfit, this.orderSendComment, this.magicNumber, 0, Red);

        if (ticket > 0) {
            Print("Sell order opened successfully with ticket #", ticket);
            return ticket;
        } else {
            Print("Failed to open sell order with error code #", GetLastError());
            return 0;
        }
    }
};

CTrade Trade(gLotSize, gMaxSlippage, gTakeProfit, gStopLoss, gMagicNumber, gOrderSendComment);

int OnInit()
  {

   return(INIT_SUCCEEDED);
  }
  

void OnDeinit(const int reason)
  {

   
  }
  

void OnTick()
  { 
   
   if (IsNewCandle())
   {       
      // Check drawdown and close if function return true. 
      bool dd = CheckDrawdown(gDrawdown);
      if (dd == true) CloseOrders();
   }
   
   // -------------------- TODELETE --------------------
   
   //int var = getLastOrderType();
   // Comment(StringFormat("Show last order type:  %G",var));
   
   // --------------------------------------------------
   
   if (IsNewCandle())
      {
      // Total Open Order Count !! 
      OrderCount = CountBotOrders() ; 
      
      if (OrderCount == 0)
      {  
          if (BuyCondition())
              {
              int buyTicket = Trade.BuyNow();
              }
      
          if (SellCondition())
              {
              int sellTicket = Trade.SellNow();
              }
       }
       
       // elif Grid Condition
       

       
       
       
       
       
       
       
       
       
       
       }
  }
//+------------------------------------------------------------------+

    
  
// Check if conditions are met for a "buy" signal  
bool BuyCondition()
{
    // Calculate RSI with a 14 period on a 1 hour timeframe
    double rsi = iRSI(Symbol(), PERIOD_H1, 14, PRICE_CLOSE, 0);
    
    // Calculate the lower Bollinger Band with a 14 period and 2 standard deviation on a 1 hour timeframe
    double bbLower = iBands(Symbol(), PERIOD_H1, 14, 2, 0, PRICE_CLOSE, MODE_LOWER, 0);
    
    // Set the price to the current Ask price
    double price = Ask;
   
    // Check if the RSI is less than 30 and the current Ask price is below the lower Bollinger Band
    if (rsi < 30 && price < bbLower)
    {
        return true;
    }
    else
    {
        return false;
    }
}



// Check if conditions are met for a "sell" signal
bool SellCondition()
{
    // Calculate RSI with a 14 period on a 1 hour timeframe
    double rsi = iRSI(Symbol(), PERIOD_H1, 14, PRICE_CLOSE, 0);
    
    // Calculate the upper Bollinger Band with a 14 period and 2 standard deviation on a 1 hour timeframe
    double bbUpper = iBands(Symbol(), PERIOD_H1, 14, 2, 0, PRICE_CLOSE, MODE_UPPER, 0);
    
    // Set the price to the current Bid price
    double price = Bid;

    // Check if the RSI is greater than 70 and the current Bid price is above the upper Bollinger Band
    if (rsi > 70 && price > bbUpper)
    {
        return true;
    }
    else
    {
        return false;
    }
}

bool IsNewCandle()
  {
   static datetime saved_candle_time;
   if(Time[0] == saved_candle_time)
      return false;
   else
      saved_candle_time = Time[0];
   return true;
  }


int CountBotOrders() 
{   
    // CountBotOrders() returns the total number of orders opened by a bot, based on the  magic number 
    int orderCount = 0;
    for (int orderPosition = OrdersTotal() - 1; orderPosition >= 0; orderPosition--) 
    {
        OrderSelect(orderPosition, SELECT_BY_POS, MODE_TRADES);
        if (OrderSymbol() != Symbol() || OrderMagicNumber() != gMagicNumber) continue;
        if (OrderSymbol() == Symbol() && OrderMagicNumber() == gMagicNumber)
        if (OrderType() == OP_SELL || OrderType() == OP_BUY) orderCount++;
    }
    return orderCount;
}


  
bool CheckDrawdown(double drawdown)
{  
    // If true : then close all trade, 
    // If false: continue the trade 
    // Convert drawdown from % to decimal
    double ddLimit = NormalizeDouble(drawdown/100, 4);
    
    double balance = AccountBalance();
    double equity = AccountEquity();
    
    if (ddLimit > NormalizeDouble(1-(equity/balance), 4))
        { return false; }
    else 
        { return true;}
}

void CloseOrders()
{
   RefreshRates();

   for (int i = (OrdersTotal() - 1); i >= 0; i--)
   {
      if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES) == false)
      {
         Print("ERROR - Unable to select the order - ", GetLastError());
         break;
      } 

      bool res = false;
      int Slippage = 5;
      double BidPrice = MarketInfo(OrderSymbol(), MODE_BID);
      double AskPrice = MarketInfo(OrderSymbol(), MODE_ASK);

      if (OrderType() == OP_BUY)
      {
         res = OrderClose(OrderTicket(), OrderLots(), BidPrice, Slippage);
      }
      else if (OrderType() == OP_SELL)
      {
         res = OrderClose(OrderTicket(), OrderLots(), AskPrice, Slippage);
      }
      
      if (res == false) Print("ERROR - Unable to close the order - ", OrderTicket(), " - ", GetLastError());
   }
}


int getLastOrderOpenPrice()
{
for(int pos = OrdersTotal()-1; pos >= 0 ; pos--) 
    if (OrderSelect(pos, SELECT_BY_POS) 
        && OrderMagicNumber() == gMagicNumber 
        && OrderSymbol() == Symbol())
            { 
                return OrderOpenPrice();
            }
 return -1 ;
}


int getLastOrderType()
{
for(int pos = OrdersTotal()-1; pos >= 0 ; pos--) 
    if (OrderSelect(pos, SELECT_BY_POS) 
        && OrderMagicNumber() == gMagicNumber 
        && OrderSymbol() == Symbol())
            { 
                return OrderType();
            }
return -1 ;
} 