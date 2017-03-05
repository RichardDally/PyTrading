@0x934efea7f017fff0;

struct Referential
{
   struct Instrument
   {
     id @0 :UInt8;
     name @1 :Text;
     isin @2 :Text;
     currencyId @3 :UInt8;
   }

  instruments @0 :List(Instrument);
}
