// #44: ACO Operand flag bit-fields (uint8_t bit-fields in an anonymous struct, unioned with
// uint16_t control_) as aco_ir.h declares them. Does GCC14 SPE keep isUndef_/isFixed_ through
// construction, copy and an array of four passed to a builder-like function?
#include <cstdint>
#include <cstdio>
#include <cstring>
struct PhysReg { uint16_t reg_b = 0; constexpr PhysReg() = default; explicit constexpr PhysReg(unsigned r) : reg_b(r << 2) {} };
struct Temp { uint32_t id_ : 24; uint32_t reg_class : 8; constexpr Temp() : id_(0), reg_class(0) {} constexpr Temp(uint32_t id, uint8_t rc) : id_(id), reg_class(rc) {} };
class Operand {
public:
   constexpr Operand() : reg_(PhysReg{128}), isTemp_(false), isFixed_(true), isPrecolored_(false), isConstant_(false), isKill_(false), isUndef_(true), isFirstKill_(false), isLateKill_(false), isClobbered_(false), isCopyKill_(false), isVectorAligned_(false), is16bit_(false), is24bit_(false), signext(false), constSize(0) {}
   explicit Operand(uint8_t type) noexcept { isUndef_ = true; data_.temp = Temp(0, type); setFixed(PhysReg{128}); }
   explicit Operand(Temp r) noexcept { data_.temp = r; if (r.id_) isTemp_ = true; else { isUndef_ = true; setFixed(PhysReg{128}); } }
   void setFixed(PhysReg reg) noexcept { isFixed_ = reg.reg_b != uint16_t(-1); isPrecolored_ = isFixed_; reg_ = reg; }
   bool isTemp() const { return isTemp_; } bool isFixed() const { return isFixed_; } bool isUndefined() const { return isUndef_; } bool isConstant() const { return isConstant_; }
   uint16_t control() const { return control_; }
private:
   union { Temp temp; uint32_t i; float f; } data_ = {Temp(0, 0)};
   PhysReg reg_;
   union {
      struct { uint8_t isTemp_ : 1; uint8_t isFixed_ : 1; uint8_t isPrecolored_ : 1; uint8_t isConstant_ : 1; uint8_t isKill_ : 1; uint8_t isUndef_ : 1;
               uint8_t isFirstKill_ : 1; uint8_t isLateKill_ : 1; uint8_t isClobbered_ : 1; uint8_t isCopyKill_ : 1; uint8_t isVectorAligned_ : 1;
               uint8_t is16bit_ : 1; uint8_t is24bit_ : 1; uint8_t signext : 1; uint8_t constSize : 2; };
      uint16_t control_ = 0;
   };
};
struct Instr { Operand ops[4]; unsigned en; };
__attribute__((noipa)) static void exp(Instr *in, Operand a, Operand b, Operand c, Operand d, unsigned en) { in->ops[0] = a; in->ops[1] = b; in->ops[2] = c; in->ops[3] = d; in->en = en; }
static void show(const char *what, const Operand &o) { std::printf("%-10s undef=%d fixed=%d temp=%d const=%d control=%04x\n", what, o.isUndefined(), o.isFixed(), o.isTemp(), o.isConstant(), o.control()); }
int main()
{
   Operand values[4];
   for (unsigned i = 0; i < 4; ++i) values[i] = Operand(uint8_t(1));
   values[0] = Operand(Temp(9, 1));
   for (unsigned i = 0; i < 4; ++i) { char n[16]; std::snprintf(n, sizeof n, "values[%u]", i); show(n, values[i]); }
   Instr in; std::memset(&in, 0xff, sizeof in);
   exp(&in, values[0], values[1], values[2], values[3], 1);
   for (unsigned i = 0; i < 4; ++i) { char n[16]; std::snprintf(n, sizeof n, "exp op%u", i); show(n, in.ops[i]); }
   std::printf("sizeof(Operand)=%zu\n", sizeof(Operand));
   return 0;
}
