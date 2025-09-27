#!/usr/bin/env python3
"""
Hierarchical Property Management Issues Category Tree
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class CategoryNode:
    """Represents a category node in the hierarchical tree"""
    name: str
    path: str
    parent: Optional[str] = None
    children: List[str] = None
    level: int = 0
    
    def __post_init__(self):
        if self.children is None:
            self.children = []

class PropertyManagementCategories:
    """Hierarchical category tree for Property Management Issues"""
    
    def __init__(self):
        self.categories = self._build_category_tree()
        self.category_paths = self._build_category_paths()
    
    def _build_category_tree(self) -> Dict[str, CategoryNode]:
        """Build the complete hierarchical category tree"""
        categories = {}
        
        # Level 0: Root
        categories['Property Management Issues'] = CategoryNode(
            name='Property Management Issues',
            path='Property Management Issues',
            level=0
        )
        
        # Level 1: Main Categories
        main_categories = [
            'Maintenance & Repairs',
            'Utilities',
            'Billing & Accounts',
            'Amenities & Services',
            'Safety & Security',
            'Neighbour Relations',
            'Cleaning & Waste',
            'Requests & Inquiries',
            'Other'
        ]
        
        for cat in main_categories:
            categories[cat] = CategoryNode(
                name=cat,
                path=f'Property Management Issues > {cat}',
                parent='Property Management Issues',
                level=1
            )
            categories['Property Management Issues'].children.append(cat)
        
        # Level 2: Subcategories for Maintenance & Repairs
        maintenance_subcats = {
            'Plumbing': ['Leaks', 'Blocked drains', 'Water pressure issues'],
            'Electrical': ['Power outage', 'Faulty lighting', 'Broken appliances'],
            'HVAC': ['Heating issues', 'Cooling/AC issues', 'Ventilation'],
            'Structural': ['Cracks/damage', 'Roof issues', 'Windows/doors'],
            'General Repairs': ['Fixtures & fittings', 'Furniture', 'Other']
        }
        
        for subcat, items in maintenance_subcats.items():
            categories[subcat] = CategoryNode(
                name=subcat,
                path=f'Property Management Issues > Maintenance & Repairs > {subcat}',
                parent='Maintenance & Repairs',
                level=2
            )
            categories['Maintenance & Repairs'].children.append(subcat)
            
            for item in items:
                categories[item] = CategoryNode(
                    name=item,
                    path=f'Property Management Issues > Maintenance & Repairs > {subcat} > {item}',
                    parent=subcat,
                    level=3
                )
                categories[subcat].children.append(item)
        
        # Level 2: Subcategories for Utilities
        utilities_subcats = ['Water Supply', 'Gas Supply', 'Electricity Supply', 'Internet/Connectivity']
        for subcat in utilities_subcats:
            categories[subcat] = CategoryNode(
                name=subcat,
                path=f'Property Management Issues > Utilities > {subcat}',
                parent='Utilities',
                level=2
            )
            categories['Utilities'].children.append(subcat)
        
        # Level 2: Subcategories for Billing & Accounts
        billing_subcats = ['Rent/Lease Payments', 'Service Charges', 'Late Fees', 'Refunds/Adjustments']
        for subcat in billing_subcats:
            categories[subcat] = CategoryNode(
                name=subcat,
                path=f'Property Management Issues > Billing & Accounts > {subcat}',
                parent='Billing & Accounts',
                level=2
            )
            categories['Billing & Accounts'].children.append(subcat)
        
        # Level 2: Subcategories for Amenities & Services
        amenities_subcats = {
            'Parking': ['Allocation requests', 'Unauthorized use', 'Access issues'],
            'Elevators/Lifts': [],
            'Gym/Pool Access': [],
            'Laundry/Other shared services': []
        }
        
        for subcat, items in amenities_subcats.items():
            categories[subcat] = CategoryNode(
                name=subcat,
                path=f'Property Management Issues > Amenities & Services > {subcat}',
                parent='Amenities & Services',
                level=2
            )
            categories['Amenities & Services'].children.append(subcat)
            
            for item in items:
                categories[item] = CategoryNode(
                    name=item,
                    path=f'Property Management Issues > Amenities & Services > {subcat} > {item}',
                    parent=subcat,
                    level=3
                )
                categories[subcat].children.append(item)
        
        # Level 2: Subcategories for Safety & Security
        safety_subcats = {
            'Access Control (keys, fobs, codes)': [],
            'Security Concerns': ['Trespassing', 'Theft', 'Vandalism'],
            'Fire Safety': [],
            'Lighting in common areas': []
        }
        
        for subcat, items in safety_subcats.items():
            categories[subcat] = CategoryNode(
                name=subcat,
                path=f'Property Management Issues > Safety & Security > {subcat}',
                parent='Safety & Security',
                level=2
            )
            categories['Safety & Security'].children.append(subcat)
            
            for item in items:
                categories[item] = CategoryNode(
                    name=item,
                    path=f'Property Management Issues > Safety & Security > {subcat} > {item}',
                    parent=subcat,
                    level=3
                )
                categories[subcat].children.append(item)
        
        # Level 2: Subcategories for Neighbour Relations
        neighbour_subcats = ['Noise Complaints', 'Pets', 'Smoking', 'General Behaviour']
        for subcat in neighbour_subcats:
            categories[subcat] = CategoryNode(
                name=subcat,
                path=f'Property Management Issues > Neighbour Relations > {subcat}',
                parent='Neighbour Relations',
                level=2
            )
            categories['Neighbour Relations'].children.append(subcat)
        
        # Level 2: Subcategories for Cleaning & Waste
        cleaning_subcats = ['Garbage Disposal', 'Recycling', 'Pest Control']
        for subcat in cleaning_subcats:
            categories[subcat] = CategoryNode(
                name=subcat,
                path=f'Property Management Issues > Cleaning & Waste > {subcat}',
                parent='Cleaning & Waste',
                level=2
            )
            categories['Cleaning & Waste'].children.append(subcat)
        
        # Level 2: Subcategories for Requests & Inquiries
        requests_subcats = [
            'General Information Request',
            'Move-in / Move-out Process',
            'Renovation/Alteration Requests',
            'Document/Certificate Requests'
        ]
        for subcat in requests_subcats:
            categories[subcat] = CategoryNode(
                name=subcat,
                path=f'Property Management Issues > Requests & Inquiries > {subcat}',
                parent='Requests & Inquiries',
                level=2
            )
            categories['Requests & Inquiries'].children.append(subcat)
        
        # Level 2: Subcategories for Other
        other_subcats = ['Suggestions', 'Compliments', 'Miscellaneous']
        for subcat in other_subcats:
            categories[subcat] = CategoryNode(
                name=subcat,
                path=f'Property Management Issues > Other > {subcat}',
                parent='Other',
                level=2
            )
            categories['Other'].children.append(subcat)
        
        return categories
    
    def _build_category_paths(self) -> Dict[str, str]:
        """Build a flat dictionary of category names to their full paths"""
        return {name: node.path for name, node in self.categories.items()}
    
    def get_category_path(self, category_name: str) -> Optional[str]:
        """Get the full path for a category name"""
        return self.category_paths.get(category_name)
    
    def get_parent_category(self, category_name: str) -> Optional[str]:
        """Get the parent category for a given category"""
        node = self.categories.get(category_name)
        return node.parent if node else None
    
    def get_children(self, category_name: str) -> List[str]:
        """Get all direct children of a category"""
        node = self.categories.get(category_name)
        return node.children if node else []
    
    def get_all_leaf_categories(self) -> List[str]:
        """Get all leaf categories (categories with no children)"""
        return [name for name, node in self.categories.items() if not node.children]
    
    def get_category_hierarchy(self, category_name: str) -> List[str]:
        """Get the full hierarchy path for a category (from root to leaf)"""
        hierarchy = []
        current = category_name
        
        while current:
            hierarchy.insert(0, current)
            current = self.get_parent_category(current)
        
        return hierarchy
    
    def find_best_category(self, text: str) -> Tuple[str, str]:
        """Find the best matching category for given text
        Returns: (category_name, category_path)
        """
        # This is a simplified matching - in production, you'd use more sophisticated NLP
        text_lower = text.lower()
        
        # Keyword mapping for better matching
        keyword_mapping = {
            'plumbing': 'Plumbing',
            'leak': 'Leaks',
            'drain': 'Blocked drains',
            'water': 'Water pressure issues',
            'electrical': 'Electrical',
            'power': 'Power outage',
            'light': 'Faulty lighting',
            'appliance': 'Broken appliances',
            'hvac': 'HVAC',
            'heating': 'Heating issues',
            'cooling': 'Cooling/AC issues',
            'ac': 'Cooling/AC issues',
            'ventilation': 'Ventilation',
            'structural': 'Structural',
            'crack': 'Cracks/damage',
            'roof': 'Roof issues',
            'window': 'Windows/doors',
            'door': 'Windows/doors',
            'maintenance': 'Maintenance & Repairs',
            'repair': 'Maintenance & Repairs',
            'utility': 'Utilities',
            'billing': 'Billing & Accounts',
            'rent': 'Rent/Lease Payments',
            'payment': 'Rent/Lease Payments',
            'amenity': 'Amenities & Services',
            'parking': 'Parking',
            'elevator': 'Elevators/Lifts',
            'lift': 'Elevators/Lifts',
            'gym': 'Gym/Pool Access',
            'pool': 'Gym/Pool Access',
            'safety': 'Safety & Security',
            'security': 'Safety & Security',
            'access': 'Access Control (keys, fobs, codes)',
            'key': 'Access Control (keys, fobs, codes)',
            'fire': 'Fire Safety',
            'noise': 'Noise Complaints',
            'neighbour': 'Neighbour Relations',
            'pet': 'Pets',
            'smoking': 'Smoking',
            'cleaning': 'Cleaning & Waste',
            'garbage': 'Garbage Disposal',
            'waste': 'Garbage Disposal',
            'recycling': 'Recycling',
            'pest': 'Pest Control',
            'request': 'Requests & Inquiries',
            'inquiry': 'Requests & Inquiries',
            'move': 'Move-in / Move-out Process',
            'renovation': 'Renovation/Alteration Requests',
            'document': 'Document/Certificate Requests',
            'suggestion': 'Suggestions',
            'compliment': 'Compliments'
        }
        
        # Find best match
        best_match = None
        best_score = 0
        
        for keyword, category in keyword_mapping.items():
            if keyword in text_lower:
                # Calculate a simple score based on keyword length and position
                score = len(keyword) + (1 if text_lower.startswith(keyword) else 0)
                if score > best_score:
                    best_score = score
                    best_match = category
        
        if best_match:
            return best_match, self.get_category_path(best_match)
        
        # Default fallback
        return 'Miscellaneous', self.get_category_path('Miscellaneous')
    
    def get_category_tree_for_ui(self) -> Dict:
        """Get the category tree formatted for UI consumption"""
        def build_tree_node(category_name: str) -> Dict:
            node = self.categories[category_name]
            return {
                'name': node.name,
                'path': node.path,
                'level': node.level,
                'children': [build_tree_node(child) for child in node.children]
            }
        
        return build_tree_node('Property Management Issues')

# Global instance
property_categories = PropertyManagementCategories()
