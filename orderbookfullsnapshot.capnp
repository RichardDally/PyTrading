@0x934efea7f017fff1;

struct OrderBookFullSnapshot
{
   enum Way
   {
      buy @0;
      sell @1;
   }

   struct OrderBookStatistics
   {
      lastPrice @0 :Float64;
      highPrice @1 :Float64;
      lowPrice @2 :Float64;
   }

   struct OrderInBook
   {
      order_identifier @0 :UInt64;
      way @1 :Way;
      quantity @2 :Float64;
      price @3 :Float64;
      counterparty @4 :Text;
      timestamp @5 :UInt64;
   }

   instrument_identifier @0 :UInt8;
   statistics @1 :OrderBookStatistics;
   bids @2 :List(OrderInBook);
   asks @3 :List(OrderInBook);
}
