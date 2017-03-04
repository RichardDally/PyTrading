@0x934efea7f017fff0;

struct Instrument
{
   id @0 :UInt8;
   name @1 :Text;
   currency @2 :Text;
   isin @3 :Text;
}

struct Referential
{
  instruments @0 :List(Instrument);
}
