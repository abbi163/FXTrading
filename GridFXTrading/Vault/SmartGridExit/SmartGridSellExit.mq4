//+------------------------------------------------------------------+
//|                                                      ProjectName |
//|                                      Copyright 2018, CompanyName |
//|                                       http://www.companyname.net |
//+------------------------------------------------------------------+

#property copyright "SmartGridSellExit"
#property version   "000.001"
#property strict



extern double gLotSize = 0.1;          // Set the lot size of the order
extern double gMaxSlippage = 10;       // Maximum slippage allowed while opening the trade
extern double gTakeProfit = 100;        // Set the take profit in points
extern double gStopLoss = 10000;       // Set the stop loss in points
extern string gOrderSendComment = "SmartGridSellExit" ;    // Order Comment
extern int gMaxOrders = 18;            // Maximum allowed Open Order
extern double gDrawdown = 100;           // allowed drawdown in percentage !!
extern double gGridStep = 250;          // Grid Steps in Points !!
extern double gAnchorPrice = 1;        // Trade will stop once Bid price above this !!
extern double gLimitPrice = 1 ;       // If trade goes opposite, after this price, bot will stop once grid is done !
extern double gDistanceSmartTP = 400 ; // If trade opened above 55 EMA 1H, then crossover not applicable if Bid > lastOpenPrice + gDistanceSmartTP * Point

double gMagicNumber = 11;      // Magic number for BotX-Sell is 11
int gAnchorFlag = 0 ;  // If AnchorFlag is 0, Trade will go on
int gLimitFlag = 0 ; // If LimitFlag = 0, Then even if a grid is over another grid will open
int gDecimalDigits ;

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
class CTrade
  {
private:
   double            lotSize;
   double            maxSlippage;
   double            takeProfit;
   double            stopLoss;
   int               magicNumber;
   string            orderSendComment;

public:
                     CTrade(double lotSize, double maxSlippage, double takeProfit, double stopLoss, int magicNumber, string orderSendComment)
     {
      this.lotSize = lotSize;
      this.maxSlippage = maxSlippage;
      this.takeProfit = takeProfit;
      this.stopLoss = stopLoss;
      this.magicNumber = magicNumber;
      this.orderSendComment = orderSendComment;
     }

   int               BuyNow()
     {
      double takeProfit = Ask + this.takeProfit * Point; // Set the take profit gTakeProfit points above the Ask price
      double stopLoss = Bid - this.stopLoss * Point; // Set the stop loss gStopLoss below Bid price

      // Open a buy order with the specified lot size, entry price, and take profit
      int ticket = OrderSend(Symbol(), OP_BUY, this.lotSize, Ask, this.maxSlippage, stopLoss, takeProfit, this.orderSendComment, this.magicNumber, 0, Blue);

      if(ticket > 0)
        {
         Print("Buy order opened successfully with ticket #", ticket);
         return ticket;
        }
      else
        {
         Print("Failed to open buy order with error code #", GetLastError());
         return 0;
        }
     }

   int               SellNow()
     {
      double takeProfit = Bid - this.takeProfit * Point; // Set the take profit TakeProfit points below the Bid price
      double stopLoss = Ask + this.stopLoss * Point; // Set the stop loss gStopLoss above Bid price

      // Open a sell order with the specified lot size, entry price, take profit, and stop loss
      int ticket = OrderSend(Symbol(), OP_SELL, this.lotSize, Bid, this.maxSlippage, stopLoss, takeProfit, this.orderSendComment, this.magicNumber, 0, Red);

      if(ticket > 0)
        {
         Print("Sell order opened successfully with ticket #", ticket);
         return ticket;
        }
      else
        {
         Print("Failed to open sell order with error code #", GetLastError());
         return 0;
        }
     }
  };

CTrade Trade(gLotSize, gMaxSlippage, gTakeProfit, gStopLoss, gMagicNumber, gOrderSendComment);

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
int OnInit()
  {
   gDecimalDigits = Digits() ;

   ObjectCreate("AnchorLine", OBJ_HLINE, 0, 0, gAnchorPrice);
   ObjectSet("AnchorLine", OBJPROP_COLOR, Red);

   ObjectCreate("LimitLine", OBJ_HLINE, 0, 0, gLimitPrice);
   ObjectSet("LimitLine", OBJPROP_COLOR, Red);


   return(INIT_SUCCEEDED);
  }


//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {


  }


//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void OnTick()
  {

   if(IsNewCandle())
     {   
     
     
         double EMA55 = iMA(_Symbol, PERIOD_H1, 55, 0, MODE_EMA, PRICE_CLOSE, 0);
         bool IsBearish = IsBearishTrend(EMA55);
         bool CrossOver = IsCrossOver(EMA55);


      if(gAnchorPrice > Ask)
        {
         gAnchorFlag = 1 ;
         CloseSymbolOrders() ;
         Comment(StringFormat("Anchor Price of %G have been Achieved. All Trades have been closed", gAnchorPrice));
        }


      if(gLimitPrice < Bid)
        {
         gLimitFlag = 1;
         Comment(StringFormat("Limit Price of %G is achieved, Once gird is closed, no new trade will open", gLimitPrice));
        }

      if(gAnchorFlag == 0)
        {
        
        
         // Get Last Open Type, Last Open Price, Open Order Count by Bot
         int lastOrderType = getLastOrderType() ;
         double lastOpenPrice = getLastOrderOpenPrice() ; 
         int OrderCount = CountBotOrders();

         // If OrderCount is 0 and gLimitFlag = 0 and IsBearish = False ! Open Trade with gTakeProfit
         if(OrderCount == 0 && gLimitFlag == 0 && IsBearish == 0) Trade.SellNow();
      
         // If OrderCount is 0 and gLimitFlag = 0 and IsBearish = True ! Open Trade without TakeProfit
         if (OrderCount == 0 && gLimitFlag ==0 && IsBearish == 1) 
         {
           double stopLoss = Ask + gStopLoss * Point; // Set the stop loss gStopLoss below Bid price
           // Open a sell order with the specified lot size, entry price, and take profit
           OrderSend(Symbol(), OP_SELL, gLotSize, Bid, gMaxSlippage, stopLoss, 0, gOrderSendComment, gMagicNumber, 0, Green);
           
         }
         
         // If OrderCount = 1, and Ask Price < OrderOpenPrice - 300 points, Close Trade . 
         if (OrderCount ==1 && CrossOver == 1)
         {
            if (Ask < lastOpenPrice - gDistanceSmartTP * Point) 
            
               {
                   CloseSymbolOrders();
                   gAnchorFlag = 1;
               }
         }
               
         
         
         // elif Grid Condition
         if (OrderCount == 1 && lastOrderType == 1 && Bid - lastOpenPrice > gGridStep * Point)
         {  
            GridOpen(lastOrderType, lastOpenPrice);
            ModifyTP(lastOrderType,  gTakeProfit, gMagicNumber);
         } 
         
         if (OrderCount > 1 )
         {  

            GridOpen(lastOrderType, lastOpenPrice);
            ModifyTP(lastOrderType,  gTakeProfit, gMagicNumber);

         }
        }

      // Check drawdown and close if function return true.
      bool dd = CheckDrawdown(gDrawdown);
      if(dd == true)
         CloseOrders();

     }
  }

//+------------------------------------------------------------------+
//|    IS NewCandle function                                         |
//+------------------------------------------------------------------+
bool IsNewCandle()
  {
   static datetime saved_candle_time;
   if(Time[0] == saved_candle_time)
      return false;
   else
      saved_candle_time = Time[0];
   return true;
  }

bool IsCrossOver(double EMA55)
   {
      if ((Close[1] > EMA55  && Close[2] < EMA55)||(Close[1] < EMA55  && Close[2] > EMA55)) return true;
      
      return false;
   }
   
bool IsBullishTrend(double EMA55)
   {
      if (Bid > EMA55) return true;
      return false;
   }

// ---------------- IsBearishTrend to be used in Sell Bot ------------------------
bool IsBearishTrend(double EMA55)
   {
      if (Ask < EMA55) return true;
      return false;
   }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
int CountBotOrders()
  {
// CountBotOrders() returns the total number of orders opened by a bot, based on the  magic number
   int orderCount = 0;
   for(int orderPosition = OrdersTotal() - 1; orderPosition >= 0; orderPosition--)
     {
      OrderSelect(orderPosition, SELECT_BY_POS, MODE_TRADES);
      if(OrderSymbol() != Symbol() || OrderMagicNumber() != gMagicNumber)
         continue;
      if(OrderSymbol() == Symbol() && OrderMagicNumber() == gMagicNumber)
         if(OrderType() == OP_SELL || OrderType() == OP_BUY)
            orderCount++;
     }
   return orderCount;
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool CheckDrawdown(double drawdown)
  {
// If true : then close all trade,
// If false: continue the trade
// Convert drawdown from % to decimal
   double ddLimit = NormalizeDouble(drawdown/100, 4);

   double balance = AccountBalance();
   double equity = AccountEquity();

   if(ddLimit > NormalizeDouble(1-(equity/balance), 4))
     { return false; }
   else
     { return true;}
  }

//+------------------------------------------------------------------+
//| CloseOrder: Close all the orders in that's live,                 |
//|             whether order was put manually or by a bot           |                                                    
//+------------------------------------------------------------------+
void CloseOrders()
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

      if(OrderType() == OP_BUY)
        {
         res = OrderClose(OrderTicket(), OrderLots(), BidPrice, Slippage);
        }
      else
         if(OrderType() == OP_SELL)
           {
            res = OrderClose(OrderTicket(), OrderLots(), AskPrice, Slippage);
           }

      if(res == false)
         Print("ERROR - Unable to close the order - ", OrderTicket(), " - ", GetLastError());
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

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
double getLastOrderOpenPrice()
  {
   for(int pos = OrdersTotal()-1; pos >= 0 ; pos--)
      if(OrderSelect(pos, SELECT_BY_POS)
         && OrderMagicNumber() == gMagicNumber
         && OrderSymbol() == Symbol())
        {
         return NormalizeDouble(OrderOpenPrice(), 5) ;
        }
   return -1 ;
  }


//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
int getLastOrderType()
  {
   for(int pos = OrdersTotal()-1; pos >= 0 ; pos--)
      if(OrderSelect(pos, SELECT_BY_POS)
         && OrderMagicNumber() == gMagicNumber
         && OrderSymbol() == Symbol())
        {
         return OrderType();
        }
   return -1 ;
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
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

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void ModifyTP(int orderType, double TakeProfit, double magicNumber)
  {
   RefreshRates();

   double totalOpenPrice = 0.0;
   int numOrders = 0;
   double newTakeProfit ;

   for(int pos = OrdersTotal() - 1; pos >= 0; pos--)
     {
      if(OrderSelect(pos, SELECT_BY_POS, MODE_TRADES))
        {
         if(OrderMagicNumber() == magicNumber && OrderType() == orderType && OrderSymbol() == Symbol())
           {
            totalOpenPrice += OrderOpenPrice();
            numOrders++;
           }
        }
     }


   double averageOpenPrice = totalOpenPrice / numOrders;

   if(orderType == 0)
     { newTakeProfit =  averageOpenPrice + TakeProfit * Point ; }

   if(orderType == 1)
     { newTakeProfit =  averageOpenPrice - TakeProfit * Point ; }

   newTakeProfit = NormalizeDouble(newTakeProfit, gDecimalDigits) ;

   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
        {
         if(OrderMagicNumber() == magicNumber && OrderType() == orderType && OrderSymbol() == Symbol())
           {

            RefreshRates();
            bool result = OrderModify(OrderTicket(), OrderOpenPrice(), OrderStopLoss(), newTakeProfit, 0, Blue);
            if(result == false)
              {
               Print("Error modifying take profit for order ", OrderTicket(), ": ", GetLastError());
              }
           }
        }
     }
  }
//+------------------------------------------------------------------+
