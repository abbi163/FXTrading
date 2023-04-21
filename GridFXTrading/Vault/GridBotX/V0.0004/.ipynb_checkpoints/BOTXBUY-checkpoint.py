
#property copyright "BOTXBUY"
#property version   "000.004"
#property strict



extern double gLotSize = 0.1;          // Set the lot size of the order
extern double gMaxSlippage = 10;       // Maximum slippage allowed while opening the trade
extern double gTakeProfit = 100;        // Set the take profit in points
extern double gStopLoss = 10000;       // Set the stop loss in points
extern string gOrderSendComment = "BUY-i-BOT" ;    // Order Comment 
extern int gMaxOrders = 18;            // Maximum allowed Open Order
extern double gDrawdown = 1;           // allowed drawdown in percentage !!
extern double gGridStep = 70;          // Grid Steps in Points !!
extern double gAnchorPrice = 1;        // Trade will stop once Bid price above this !! 
extern double gLimitPrice = 1 ;       // If trade goes opposite, after this price, bot will stop once grid is done !


double gMagicNumber = 10;      // Magic number for BotX-Buy is 10
int gAnchorFlag = 0 ;  // If AnchorFlag is 0, Trade will go on
int gLimitFlag = 0 ; // If LimitFlag = 0, Then even if a grid is over another grid will open
int gDecimalDigits ;

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
   gDecimalDigits = Digits() ;
   
   ObjectCreate("AnchorLine", OBJ_HLINE, 0, 0, gAnchorPrice); 
   ObjectSet("AnchorLine", OBJPROP_COLOR, Red);

   ObjectCreate("LimitLine", OBJ_HLINE, 0, 0, gLimitPrice); 
   ObjectSet("LimitLine", OBJPROP_COLOR, Red);
   
   return(INIT_SUCCEEDED);
  }
  

void OnDeinit(const int reason)
  {

   
  }
  

void OnTick()
  { 
      
      
   if (IsNewCandle())
      {
      
      if (gAnchorPrice < Bid)
         {
         gAnchorFlag = 1 ;
         CloseSymbolOrders() ;
         Comment(StringFormat("Anchor Price of %G have been Achieved. All Trades have been closed", gAnchorPrice));
         }
         
      if (gLimitPrice > Ask)
         {
         gLimitFlag = 1;
         Comment(StringFormat("Limit Price of %G have been achieved. Once grid is done, no new trades will be open", gLimitPrice));
         } 
      
      if (gAnchorFlag == 0)
      
      {
         // Total Open Order Count !! 
         int OrderCount = CountBotOrders() ; 
     
         if (OrderCount == 0 && gLimitFlag ==0)
         {  
            int buyTicket = Trade.BuyNow();     
         }
          
         // elif Grid Condition
         if (OrderCount > 0)
         {  
            int lastOrderType = getLastOrderType() ;
            double lastOpenPrice = getLastOrderOpenPrice() ;
            
            GridOpen(lastOrderType, lastOpenPrice);
            ModifyTP(lastOrderType,  gTakeProfit, gMagicNumber);
         
            // -------------------- TODELETE --------------------
            // int lastOrderType = getLastOrderType();
            // double x= lastOpenPrice  ;
            // double y = Ask ;
            // double z = x - y ;
            
            // Comment(StringFormat("Last Order Open price :  %G , Ask Price: %G , Diff : % G",x, y, z * Point));
            // --------------------------------------------------
         } 
       }
      // Check drawdown and close if function return true. 
      bool dd = CheckDrawdown(gDrawdown);
      if (dd == true) CloseOrders();
 
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

//+------------------------------------------------------------------+
//|CloseSymbolOrder() : Only close the order with this symbol        |
//|                     and the one put by this bot.                 |                                                 
//+------------------------------------------------------------------+

void CloseSymbolOrders()
  {
   RefreshRates();

   for(int i = (OrdersTotal() - 1); i >= 0; i--)
     {
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES) == false)
        {
         Print("ERROR - Unable to select the order - ", GetLastError());
         break;
        }

      bool res = false;
      int Slippage = 5;
      double BidPrice = MarketInfo(OrderSymbol(), MODE_BID);
      double AskPrice = MarketInfo(OrderSymbol(), MODE_ASK);

      if(OrderType() == OP_BUY && OrderMagicNumber() == gMagicNumber && OrderSymbol() == Symbol())
        {
         res = OrderClose(OrderTicket(), OrderLots(), BidPrice, Slippage);
        }
      else
         if(OrderType() == OP_SELL && OrderMagicNumber() == gMagicNumber && OrderSymbol() == Symbol())
           {
            res = OrderClose(OrderTicket(), OrderLots(), AskPrice, Slippage);
           }

      if(res == false)
         Print("ERROR - Unable to close the order - ", OrderTicket(), " - ", GetLastError());
     }
  }


double getLastOrderOpenPrice()
{
for(int pos = OrdersTotal()-1; pos >= 0 ; pos--) 
    if (OrderSelect(pos, SELECT_BY_POS) 
        && OrderMagicNumber() == gMagicNumber 
        && OrderSymbol() == Symbol())
            { 
                return NormalizeDouble(OrderOpenPrice(), 5) ;
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



void GridOpen(int lastOrderType, double lastOpenPrice)
{
    RefreshRates();
    
    if(lastOrderType == 0 && lastOpenPrice - Ask > gGridStep * Point)
        {
            int buyTicket = Trade.BuyNow();
        }

    if(lastOrderType == 1 && Bid - lastOpenPrice > gGridStep * Point)
        {
            int sellTicket = Trade.SellNow();
        }
}



void ModifyTP(int orderType, double TakeProfit, double magicNumber)
{  
   RefreshRates();

   double totalOpenPrice = 0.0;
   int numOrders = 0;
   double newTakeProfit ;
   
   for (int pos = OrdersTotal() - 1; pos >= 0; pos--)
   {
      if (OrderSelect(pos, SELECT_BY_POS, MODE_TRADES))
      {
         if (OrderMagicNumber() == magicNumber && OrderType() == orderType && OrderSymbol() == Symbol())
         {
            totalOpenPrice += OrderOpenPrice();
            numOrders++;
         }
      }
   }
   

      double averageOpenPrice = totalOpenPrice / numOrders;
       
      if (orderType == 0)
          { newTakeProfit =  averageOpenPrice + TakeProfit * Point ; }
      
      if (orderType == 1)
         { newTakeProfit =  averageOpenPrice - TakeProfit * Point ; }
   
    newTakeProfit = NormalizeDouble(newTakeProfit, gDecimalDigits) ;
    
    for (int i = OrdersTotal() - 1; i >= 0; i--)
       {
          if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
          {
             if (OrderMagicNumber() == magicNumber && OrderType() == orderType && OrderSymbol() == Symbol())
             {  
             
                RefreshRates();
                bool result = OrderModify(OrderTicket(), OrderOpenPrice(), OrderStopLoss(), newTakeProfit, 0, Blue);
                if (result == false)
                {
                   Print("Error modifying take profit for order ", OrderTicket(), ": ", GetLastError());
                }
             }
          }
       }
}


