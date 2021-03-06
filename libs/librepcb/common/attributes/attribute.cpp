/*
 * LibrePCB - Professional EDA for everyone!
 * Copyright (C) 2013 LibrePCB Developers, see AUTHORS.md for contributors.
 * http://librepcb.org/
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/*****************************************************************************************
 *  Includes
 ****************************************************************************************/
#include <QtCore>
#include "attribute.h"
#include "attributetype.h"
#include "attributeunit.h"

/*****************************************************************************************
 *  Namespace
 ****************************************************************************************/
namespace librepcb {

/*****************************************************************************************
 *  Constructors / Destructor
 ****************************************************************************************/

Attribute::Attribute(const Attribute& other) noexcept :
    mKey(other.mKey), mType(other.mType), mValue(other.mValue), mUnit(other.mUnit)
{
}

Attribute::Attribute(const SExpression& node) :
    mKey("UNKNOWN"), // backward compatibility - remove this some time!
    mType(&AttributeType::fromString(node.getValueByPath<QString>("type"))),
    mValue(node.getValueByPath<QString>("value")),
    mUnit(mType->getUnitFromString(node.getValueByPath<QString>("unit")))
{
    // backward compatibility - remove this some time!
    QString key = node.getChildByIndex(0).getValue<QString>(true);
    key.replace(".", "_");
    key.replace("-", "_");
    mKey = key.toUpper();

    // backward compatibility - remove this some time!
    mValue.replace(QRegularExpression("#([_A-Za-z][_\\|0-9A-Za-z]*)"), "{{\\1}}");
    mValue.replace(QRegularExpression("\\{\\{(\\w+)\\|(\\w+)\\}\\}"), "{{ \\1 or \\2 }}");

    if (!checkAttributesValidity()) throw LogicError(__FILE__, __LINE__);
}

Attribute::Attribute(const AttributeKey& key, const AttributeType& type, const QString& value,
                     const AttributeUnit* unit) :
    mKey(key), mType(&type), mValue(value), mUnit(unit)
{
    if (!checkAttributesValidity()) throw LogicError(__FILE__, __LINE__);
}

Attribute::~Attribute() noexcept
{
}

/*****************************************************************************************
 *  Getters
 ****************************************************************************************/

QString Attribute::getValueTr(bool showUnit) const noexcept
{
    return mType->printableValueTr(mValue, showUnit ? mUnit : nullptr);
}

/*****************************************************************************************
 *  Setters
 ****************************************************************************************/

void Attribute::setTypeValueUnit(const AttributeType& type, const QString& value,
                                 const AttributeUnit* unit)
{
    if ((!type.isUnitAvailable(unit)) || (!type.isValueValid(value))) {
        throw LogicError(__FILE__, __LINE__, QString("%1,%2,%3")
        .arg(type.getName(), value, unit ? unit->getName() : "-"));
    }
    mType = &type;
    mValue = value;
    mUnit = unit;
}

/*****************************************************************************************
 *  General Methods
 ****************************************************************************************/

void Attribute::serialize(SExpression& root) const
{
    if (!checkAttributesValidity()) throw LogicError(__FILE__, __LINE__);
    root.appendChild(mKey);
    root.appendChild("type", *mType, false);
    if (mUnit) {
        root.appendChild("unit", *mUnit, false);
    } else {
        root.appendChild("unit", SExpression::createToken("none"), false);
    }
    root.appendChild("value", mValue, false);
}

/*****************************************************************************************
 *  Operator Overloadings
 ****************************************************************************************/

bool Attribute::operator==(const Attribute& rhs) const noexcept
{
    if (mKey != rhs.mKey)       return false;
    if (mType != rhs.mType)     return false;
    if (mValue != rhs.mValue)   return false;
    if (mUnit != rhs.mUnit)     return false;
    return true;
}

/*****************************************************************************************
 *  Private Methods
 ****************************************************************************************/

bool Attribute::checkAttributesValidity() const noexcept
{
    if (!mType->isUnitAvailable(mUnit))     return false;
    if (!mType->isValueValid(mValue))       return false;
    return true;
}

/*****************************************************************************************
 *  End of File
 ****************************************************************************************/

} // namespace librepcb
