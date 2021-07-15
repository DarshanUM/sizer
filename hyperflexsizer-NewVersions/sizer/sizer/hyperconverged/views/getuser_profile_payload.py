GET_USER_PROFILE = '''
<soapenv:Envelope
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <soapenv:Body>
        <cisco:GetCustomerPartyMaster
            xmlns:oa="http://www.openapplications.org/oagis/9"
            xmlns:cisco="urn:cisco:b2b:bod:services:1.0"
            xmlns:b2b="urn:cisco:b2bngc:services:1.0">
            <oa:ApplicationArea>
                <oa:Sender>
                    <oa:LogicalID>12</oa:LogicalID>
                    <oa:ComponentID>B2B-2.0</oa:ComponentID>
                    <oa:ReferenceID>Cisco Systems</oa:ReferenceID>
                </oa:Sender>
                <oa:Receiver>
                    <oa:LogicalID>12</oa:LogicalID>
                    <oa:ID>Cisco Systems</oa:ID>
                </oa:Receiver>
                <oa:CreationDateTime>1967-08-13</oa:CreationDateTime>
                <oa:BODID schemeVersionID="1.0" schemeAgencyName="Cisco">normalizedString</oa:BODID>
            </oa:ApplicationArea>
        </cisco:GetCustomerPartyMaster>
    </soapenv:Body>
</soapenv:Envelope>'''