//+------------------------------------------------------------------+
//|                                                 TurboScalper.mq4 |
//|                                                   Abhijeet Anand |
//|             https://www.linkedin.com/in/abhijeet-anand-9b411781/ |
//+------------------------------------------------------------------+
#property strict
#property version   "0.001"

extern double gLotSize = 0.1;                                   // Set the lot size of the order
extern double gMaxSlippage = 10;                                // Maximum slippage allowed while opening the trade
extern double gTakeProfit = 100;                                // Set the take profit in points
extern double gStopLoss = 10000;                                // Set the stop loss in points
extern double gMagicNumber = 123;                               // Magic number for opening the trade
extern string gOrderSendComment = "AlphaGrid V 0.005" ;         // Order Comment 
extern  ENUM_TIMEFRAMES  gTimeFrame = PERIOD_M5 ;                      // TimeFrame for Fast and Slow Moving Average
extern  ENUM_TIMEFRAMES gAnchorTimeFrame = PERIOD_D1 ;                 // TimeFrame for Anchor Time ! Default 1 Day


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
   int OrderCount = CountBotOrders() ; 
   double EMA200D = iMA(_Symbol, gAnchorTimeFrame, 200, 0, MODE_EMA, PRICE_CLOSE, 0);
   double SlowEMA = iMA(_Symbol, gTimeFrame, 200, 0, MODE_EMA, PRICE_CLOSE, 0);
   double FastEMA = iMA(_Symbol, gTimeFrame,  50, 0, MODE_EMA, PRICE_CLOSE, 0);
   double SlowEMA_Shift1 = iMA(_Symbol, gTimeFrame, 200, 0, MODE_EMA, PRICE_CLOSE, 1);
   double FastEMA_Shift1 = iMA(_Symbol, gTimeFrame,  50, 0, MODE_EMA, PRICE_CLOSE, 1);


   if (OrderCount == 0)
   {  
      if (BuyCondition(EMA200D, SlowEMA, FastEMA, SlowEMA_Shift1, FastEMA_Shift1))
         {
         int buyTicket = Trade.BuyNow();
         }
      
      if (SellCondition(EMA200D, SlowEMA, FastEMA, SlowEMA_Shift1, FastEMA_Shift1))
         {
         int sellTicket = Trade.SellNow();
         }
   }

 /*  
   if (OrderCount > 0)
   {
      int LastOrderType = getLastOrderType();
      
      if (LastOrderType == 0) 
         {
            if (CloseBuy(SlowEMA, FastEMA)) CloseOrders();
         }
      
      if (LastOrderType == 1) 
         {
            if (CloseSell(SlowEMA, FastEMA)) CloseOrders();
         }
   }
   
*/   
   
   }
}



bool BuyCondition(double EMA200D, double SlowEMA, double FastEMA, double SlowEMA_Shift1, double FastEMA_Shift1)
{
    // 1. if Ask price is Above 200 Daily EMA
    // 2. if FastEMA is greater than SlowEMA (Golden Cross)
    if (Ask > EMA200D)
      {
      if (FastEMA > SlowEMA && FastEMA_Shift1 < SlowEMA_Shift1) return true;         
      else return false;
      }
   return false;
} 

bool SellCondition(double EMA200D, double SlowEMA, double FastEMA, double SlowEMA_Shift1, double FastEMA_Shift1)
{
    // 1. if Bid price is below 200 Daily EMA
    // 2. if FastEMA is less than SlowEMA (Death Cross)
    if (Bid < EMA200D)
      {
      if (FastEMA < SlowEMA && FastEMA_Shift1 > SlowEMA_Shift1) return true;         
      else return false;
      }
   return false;
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


/*
bool CloseBuy(double SlowEMA, double FastEMA)
{
   
   if (FastEMA < SlowEMA ) return true;         
   else return false;
}

bool CloseSell(double SlowEMA, double FastEMA)
{
   
   if (FastEMA > SlowEMA ) return true;         
   else return false;
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



*/


// TODO: Make RISK PER TRADE AS PERCENTAGE OF EQUITY !!
// TODO : ADD MARTINGLE FEATURE TOO. 