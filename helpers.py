def get_apn_details(cp):
    """
    Extract APN details from a CP record
    
    Args:
        cp: A CP model instance
    
    Returns:
        A list of dictionaries containing APN details
    """
    apn_details = []
    
    # Map of CP fields to their related APN object and quantity
    apn_mappings = [
        {'apn': cp.apn1, 'quantity': cp.Qte_1, 'id_field': 'PIN1_ID'},
        {'apn': cp.apn2, 'quantity': cp.Qte_2, 'id_field': 'PIN2_ID'},
        {'apn': cp.apn3, 'quantity': cp.Qte_3, 'id_field': 'PIN3_ID'},
        {'apn': cp.apn4, 'quantity': cp.QTE_4, 'id_field': 'PIN4_ID'},
        {'apn': cp.apn5, 'quantity': cp.Qte_Tige_1, 'id_field': 'TIGE_1_ID'},
        {'apn': cp.apn6, 'quantity': cp.Qte_Tige_2, 'id_field': 'TIGE_2_ID'},
        {'apn': cp.apn7, 'quantity': None, 'id_field': 'RESSORT_1_ID'},
        {'apn': cp.apn8, 'quantity': None, 'id_field': 'RESSORT_2_ID'},
    ]
    
    # For each mapping, if APN exists, add its details to the results
    for mapping in apn_mappings:
        if mapping['apn'] and getattr(cp, mapping['id_field']):
            apn_detail = {
                'id': mapping['apn'].PIN_id,
                'dpn': mapping['apn'].DPN,
                'type': mapping['apn'].Type,
                'quantity': mapping['quantity'],
                'image': mapping['apn'].Image,
                'ref_emdep': mapping['apn'].Ref_Emdep,
                'ref_ingun': mapping['apn'].Ref_Ingun,
                'ref_fenmmital': mapping['apn'].Ref_Fenmmital,
                'ref_ptr': mapping['apn'].Ref_Ptr,
                'multi_apn': mapping['apn'].Multi_APN,
                'location': mapping['apn'].Location
            }
            apn_details.append(apn_detail)
    
    return apn_details

def parse_location(location_str):
    """
    Parse a location string into cabinet and drawer components
    
    Args:
        location_str: A string in format "ARMOIRE X-YY" where X is the cabinet and YY is the drawer
        
    Returns:
        A dictionary with 'cabinet' and 'drawer' keys, or None if parsing fails
    """
    if not location_str:
        return None
        
    try:
        # Remove "ARMOIRE " prefix if it exists
        if "ARMOIRE " in location_str:
            location_str = location_str.replace("ARMOIRE ", "")
            
        # Split by hyphen
        parts = location_str.split('-')
        if len(parts) == 2:
            cabinet = parts[0].strip()
            drawer = parts[1].strip()
            return {
                'cabinet': cabinet,
                'drawer': drawer,
                'full_location': location_str
            }
    except Exception:
        pass
        
    return None
