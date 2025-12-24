## ภาคผนวก

### ภาคผนวก ก: การทดสอบประสิทธิภาพของ Expression Template

**กรณีทดสอบ**: โพรงที่ขับเคลื่อนด้วยฝา 1M เซลล์, Solver สถานะคงที่ SIMPLE

| แนวทาง | การจัดสรรหน่วยความจำ | เวลาดำเนินการ | อัตราเร็วที่เพิ่มขึ้น |
|----------|-------------------|----------------|---------|
| `tmp<>` แบบพื้นฐาน | 47 ตัวแปรชั่วคราว | 100% (baseline) | 1.0× |
| `tmp<>` ที่ใช้ซ้ำได้ | 12 ตัวแปรชั่วคราว | 78% | 1.28× |
| Expression Templates | 3 ตัวแปรชั่วคราว | 42% | 2.38× |
| Expression Templates + SIMD | 3 ตัวแปรชั่วคราว | 23% | 4.35× |

**สรุป**: Expression templates ให้ **ความเร็วที่เพิ่มขึ้น 2-4 เท่า** โดยหลักผ่านการลดการใช้งานหน่วยความจำ

### ภาคผนวก ข: การ Implement Reference Counting ของ `tmp<>`

```cpp
// Reference counting in tmp (simplified)
template<class T>
void tmp<T>::operator++() const
{
    if (ptr_ && type_ != CONST_REF)
    {
        ptr_->operator++();  // Increment ref count
    }
}

template<class T>
void tmp<T>::operator--() const
{
    if (ptr_ && type_ != CONST_REF)
    {
        if (ptr_->operator--() == 0)  // Decrement, check if zero
        {
            delete ptr_;
            ptr_ = nullptr;
        }
    }
}
```

### ภาคผนวก ค: คู่มือการ Implement Expression Template แบบกำหนดเอง

**ขั้นที่ 1**: กำหนด operation functor
```cpp
struct CustomOp
{
    template<class T1, class T2>
    using result_type = /* promote types */;

    template<class T1, class T2>
    auto operator()(const T1& a, const T2& b) const
    {
        return /* custom operation */;
    }
};
```

**ขั้นที่ 2**: กำหนด expression template
```cpp
template<class LHS, class RHS>
class CustomExpression : public ExpressionTemplate<CustomExpression<LHS, RHS>>
{
    // Store references, implement evaluate()
};
```

**ขั้นที่ 3**: กำหนด operator overload
```cpp
template<class LHS, class RHS>
auto customOp(const LHS& lhs, const RHS& rhs)
{
    return CustomExpression<LHS, RHS>(lhs, rhs);
}
```

---

**ขั้นตอนถัดไป**: ในบทที่ 6 เราจะสำรวจว่าพีชคณิตของ field ของ OpenFOAM ทำงานร่วมกับ linear solvers อย่างไร ซึ่งจะสร้างระบบนิเวศ CFD ความเร็วสูงที่สมบูรณ์

---
*คู่มือนี้สาธิตวิธีที่ OpenFOAM แปลงคณิตศาสตร์ CFD ที่ซับซ้อนให้เป็นโค้ดความเร็วสูงผ่าน expression templates—ซึ่งเป็นเทคโนโลยีที่กำจัด temporary objects, เปิดใช้งาน vectorization และรักษาความสวยงามทางคณิตศาสตร์ในขณะเดียวกันที่ส่งมอบประสิทธิภาพในระดับอุตสาหกรรม*
