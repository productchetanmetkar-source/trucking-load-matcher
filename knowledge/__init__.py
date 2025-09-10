"""
Comprehensive Trucking Industry Knowledge Base
Based on the data requirements document for logistics voice agent
"""

class TruckingKnowledgeBase:
    """
    Central knowledge base for trucking industry terminology, classifications,
    and mappings to improve AI agent accuracy
    """
    
    def __init__(self):
        self.truck_classifications = self._load_truck_classifications()
        self.location_mappings = self._load_location_mappings()
        self.terminology_dictionary = self._load_terminology_dictionary()
        self.conversation_patterns = self._load_conversation_patterns()
        self.rate_intelligence = self._load_rate_intelligence()
    
    def _load_truck_classifications(self):
        """Load truck type classifications and variations"""
        return {
            "container": {
                "aliases": ["full body", "closed body", "box", "cantener", "container truck"],
                "lengths": [20, 22, 24, 32, 40],
                "tonnage_ranges": {
                    "6_wheeler": [7.5, 8, 9, 10, 12],
                    "10_wheeler": [15, 16, 18, 18.5, 19, 20, 21, 22],
                    "12_wheeler": [20, 21, 22, 24, 25]
                },
                "common_sizes": [
                    {"tonnage": "7.5", "length": 17, "wheels": 6},
                    {"tonnage": "7.5", "length": 19, "wheels": 6},
                    {"tonnage": "7.5", "length": 20, "wheels": 6},
                    {"tonnage": "8", "length": 19, "wheels": 6},
                    {"tonnage": "9", "length": 20, "wheels": 6},
                    {"tonnage": "15", "length": 32, "wheels": 10},
                    {"tonnage": "25", "length": 32, "wheels": 12}
                ]
            },
            "open": {
                "aliases": ["half body", "open body", "tata body", "open truck", "open vehicle"],
                "lengths": [14, 17, 19, 20, 22, 24, 30, 32],
                "tonnage_ranges": {
                    "6_wheeler": [7.5, 8, 9],
                    "10_wheeler": [15, 16, 18, 19, 20],
                    "12_wheeler": [20, 24, 25]
                },
                "common_sizes": [
                    {"tonnage": "7.5", "length": 14, "wheels": 6},
                    {"tonnage": "7.5", "length": 17, "wheels": 6},
                    {"tonnage": "7.5", "length": 19, "wheels": 6},
                    {"tonnage": "8", "length": 19, "wheels": 6},
                    {"tonnage": "9", "length": 19, "wheels": 6},
                    {"tonnage": "19", "length": 30, "wheels": 10},
                    {"tonnage": "25", "length": 30, "wheels": 12}
                ]
            },
            "trailer": {
                "aliases": ["patta", "semi-trailer", "multi-axle", "MXL", "multi-axle container", "MAV"],
                "lengths": [32, 40, 45],
                "tonnage_ranges": {
                    "single_axle": [14.5, 15, 18, 19, 20],
                    "multi_axle": [24, 25, 30, 32, 40, 45]
                },
                "common_sizes": [
                    {"tonnage": "32", "length": 32, "axle": "single"},
                    {"tonnage": "25", "length": 32, "axle": "multi"},
                    {"tonnage": "30", "length": 32, "axle": "multi"},
                    {"tonnage": "40", "length": 40, "axle": "multi"}
                ]
            },
            "lcv": {
                "aliases": ["light commercial vehicle", "tempo", "small truck", "mini truck", "chota hathi"],
                "lengths": [8, 10, 12, 14],
                "tonnage_ranges": {"light": [1, 1.5, 2, 2.5, 3, 4, 5]},
                "common_sizes": [
                    {"tonnage": "1", "length": 8, "type": "tempo"},
                    {"tonnage": "2", "length": 10, "type": "mini_truck"},
                    {"tonnage": "3", "length": 12, "type": "small_truck"}
                ]
            },
            "hmv": {
                "aliases": ["heavy motor vehicle", "big truck", "heavy truck"],
                "lengths": [20, 22, 24, 32, 40],
                "tonnage_ranges": {"heavy": [15, 20, 25, 30, 40, 45, 50]},
                "common_sizes": [
                    {"tonnage": "25", "length": 32, "category": "heavy"},
                    {"tonnage": "40", "length": 40, "category": "heavy"}
                ]
            },
            "specialized": {
                "refrigerated": {
                    "aliases": ["reefer", "cold storage truck", "refrigerated truck"],
                    "temperature_ranges": ["-18°C to +25°C"],
                    "common_sizes": [
                        {"tonnage": "9", "length": 19, "temp": "frozen"},
                        {"tonnage": "15", "length": 32, "temp": "chilled"}
                    ]
                },
                "tanker": {
                    "aliases": ["liquid carrier", "fuel truck", "chemical tanker"],
                    "capacity_ranges": [10000, 15000, 20000, 25000, 30000],  # liters
                    "types": ["fuel", "chemical", "food_grade", "water"]
                },
                "flatbed": {
                    "aliases": ["platform truck", "open platform", "flatbed truck"],
                    "lengths": [20, 32, 40],
                    "load_types": ["machinery", "pipes", "construction_material"]
                },
                "odc": {
                    "aliases": ["over dimensional cargo", "over-size load", "heavy haul"],
                    "special_permits": ["state_permit", "police_escort", "route_survey"],
                    "equipment": ["hydraulic_trailer", "modular_trailer"]
                }
            }
        }
    
    def _load_location_mappings(self):
        """Load location variations and mappings"""
        return {
            "major_cities": {
                "bangalore": {
                    "primary": "Bangalore",
                    "aliases": ["bengaluru", "bangaluru", "banglore", "bengalore"],
                    "areas": ["electronic_city", "whitefield", "koramangala", "indiranagar"],
                    "nearby": ["hosur", "tumkur", "mysore", "salem"],
                    "state": "Karnataka",
                    "industrial_areas": ["peenya", "bommanahalli", "electronics_city"]
                },
                "mumbai": {
                    "primary": "Mumbai", 
                    "aliases": ["bombay", "mumbay", "mumbi"],
                    "areas": ["andheri", "bandra", "thane", "navi_mumbai"],
                    "nearby": ["pune", "nashik", "aurangabad", "nagpur"],
                    "state": "Maharashtra",
                    "industrial_areas": ["midc_andheri", "bhiwandi", "turbhe"]
                },
                "chennai": {
                    "primary": "Chennai",
                    "aliases": ["madras", "channai", "chenai"],
                    "areas": ["guindy", "chrompet", "tambaram", "ambattur"],
                    "nearby": ["coimbatore", "salem", "tiruchirappalli", "madurai"],
                    "state": "Tamil Nadu",
                    "industrial_areas": ["ambattur", "oragadam", "sriperumbudur"]
                },
                "delhi": {
                    "primary": "Delhi",
                    "aliases": ["new_delhi", "dilli", "delhi_ncr"],
                    "areas": ["gurgaon", "noida", "faridabad", "ghaziabad"],
                    "nearby": ["chandigarh", "jaipur", "agra", "lucknow"],
                    "state": "Delhi",
                    "industrial_areas": ["okhla", "mayapuri", "wazirpur", "naraina"]
                },
                "pune": {
                    "primary": "Pune",
                    "aliases": ["poona", "punay"],
                    "areas": ["hinjewadi", "magarpatta", "aundh", "kharadi"],
                    "nearby": ["mumbai", "nashik", "aurangabad", "kolhapur"],
                    "state": "Maharashtra",
                    "industrial_areas": ["chakan", "ranjangaon", "talegaon"]
                },
                "hyderabad": {
                    "primary": "Hyderabad",
                    "aliases": ["hyd", "hydrabad", "secunderabad"],
                    "areas": ["hitech_city", "gachibowli", "madhapur", "kondapur"],
                    "nearby": ["warangal", "nizamabad", "karimnagar", "vijayawada"],
                    "state": "Telangana",
                    "industrial_areas": ["pashamylaram", "medchal", "jeedimetla"]
                },
                "coimbatore": {
                    "primary": "Coimbatore",
                    "aliases": ["kovai", "coimbtore", "coimbator"],
                    "areas": ["peelamedu", "singanallur", "saravanampatti"],
                    "nearby": ["tirupur", "erode", "salem", "pollachi"],
                    "state": "Tamil Nadu",
                    "industrial_areas": ["kurichi", "kalapatti", "periyanaickenpalayam"]
                }
            },
            "route_landmarks": {
                "highways": {
                    "nh44": ["delhi", "gurgaon", "jaipur", "udaipur", "ahmedabad", "mumbai", "pune", "bangalore", "chennai"],
                    "nh48": ["delhi", "gurgaon", "jaipur", "udaipur", "ahmedabad", "mumbai"],
                    "nh4": ["mumbai", "pune", "bangalore", "chennai"],
                    "nh7": ["varanasi", "jabalpur", "nagpur", "hyderabad", "bangalore"]
                },
                "toll_plazas": ["panipat", "mathura", "kota", "chittorgarh"],
                "truck_stops": ["dhaba", "truck_adda", "transport_nagar"],
                "borders": ["state_border", "check_post", "octroi"]
            }
        }
    
    def _load_terminology_dictionary(self):
        """Load industry terminology and slang"""
        return {
            "truck_brands": {
                "tata": ["407", "709", "1109", "signa", "prima"],
                "ashok_leyland": ["AL", "leyland", "dost", "partner", "captain"],
                "mahindra": ["bolero", "maxi_truck", "supro", "jeeto"],
                "force": ["tempo", "light_truck", "traveller"],
                "bharat_benz": ["BB", "mercedes_truck", "1617", "2523"],
                "volvo": ["premium_truck", "fm", "fh"],
                "eicher": ["pro_series", "skyline", "medium_truck"],
                "isuzu": ["d_max", "npr", "light_truck"],
                "sml": ["swaraj_mazda", "isuzu_sml"]
            },
            "cargo_materials": {
                "fmcg": ["fast_moving_consumer_goods", "packaged_goods", "branded_products"],
                "pharmaceutical": ["medicines", "healthcare_products", "api", "tablets"],
                "textiles": ["cloth", "garments", "fabric", "yarn", "cotton"],
                "electronics": ["it_goods", "appliances", "mobile", "computer", "tv"],
                "cement": ["construction_material", "building_supplies", "acc", "ultratech"],
                "steel": ["iron", "metal_goods", "tmt_bars", "sheets", "coils"],
                "food_grains": ["agricultural_products", "commodities", "rice", "wheat", "dal"],
                "machinery": ["heavy_equipment", "industrial_goods", "pumps", "motors"],
                "automotive": ["car_parts", "auto_components", "spare_parts", "tyres"],
                "chemicals": ["industrial_chemicals", "petrochemicals", "fertilizers", "acids"]
            },
            "commercial_terms": {
                "rate_terms": {
                    "bhada": "freight_rate",
                    "rate": "price_per_km_or_total",
                    "per_km": "rate_per_kilometer", 
                    "lump_sum": "total_package_rate",
                    "market_rate": "current_standard_rate",
                    "advance": "booking_amount_token",
                    "diesel": "fuel_cost",
                    "extra": "additional_charges",
                    "detention": "waiting_charges",
                    "loading": "pickup_charges",
                    "unloading": "delivery_charges"
                },
                "urgency_indicators": {
                    "urgent": "immediate_requirement",
                    "asap": "as_soon_as_possible",
                    "today_itself": "same_day_delivery",
                    "emergency": "critical_priority",
                    "running": "vehicle_currently_moving"
                },
                "location_terms": {
                    "godown": "warehouse",
                    "factory": "manufacturing_unit", 
                    "port": "harbor_dock",
                    "railway_station": "goods_yard",
                    "market": "mandi_wholesale",
                    "border": "state_boundary_checkpost"
                }
            }
        }
    
    def _load_conversation_patterns(self):
        """Load common conversation patterns and intents"""
        return {
            "greeting_patterns": [
                "hello i need a load",
                "any load available", 
                "load chahiye",
                "i saw a load from x to y",
                "load available hai kya"
            ],
            "truck_description_patterns": [
                "22 foot container",
                "32 feet ka container hai", 
                "open truck 12 ton",
                "multi-axle vehicle",
                "trailer available hai"
            ],
            "rate_discussion_patterns": [
                "what's the rate",
                "kitna doge",
                "market rate kya hai", 
                "is it negotiable",
                "advance kitna dena padega"
            ],
            "location_patterns": [
                "mumbai se delhi",
                "bangalore to chennai",
                "from x to y route",
                "pickup location",
                "delivery point"
            ],
            "urgency_patterns": [
                "urgent chahiye",
                "today itself",
                "asap required",
                "emergency load",
                "immediate pickup"
            ],
            "rejection_patterns": [
                "rate kam hai",
                "distance zyada hai", 
                "material nahi lenge",
                "route nahi jaata",
                "truck busy hai"
            ],
            "confirmation_patterns": [
                "load confirm",
                "booking pakka",
                "advance dedo",
                "when to reach",
                "loading time kya hai"
            ]
        }
    
    def _load_rate_intelligence(self):
        """Load rate intelligence and market data"""
        return {
            "base_rates_per_km": {
                "container_7.5t": {"min": 25, "max": 35, "avg": 30},
                "container_25t": {"min": 45, "max": 65, "avg": 55},
                "open_8t": {"min": 22, "max": 32, "avg": 27},
                "trailer_32t": {"min": 55, "max": 75, "avg": 65}
            },
            "route_multipliers": {
                "mumbai_delhi": 1.2,  # High demand route
                "bangalore_chennai": 1.0,  # Standard route
                "pune_mumbai": 0.9,  # Short distance
                "chennai_bangalore": 1.1   # Good return loads
            },
            "seasonal_factors": {
                "festive_season": 1.3,  # Diwali, Eid periods
                "monsoon": 1.2,         # Rainy season premium
                "harvest_season": 1.4,  # Agricultural transport
                "normal": 1.0
            },
            "fuel_impact": {
                "diesel_price_range": {"low": 85, "high": 105},  # Rs per liter
                "rate_adjustment_per_rupee": 0.5  # Rate change per Re 1 fuel change
            }
        }
    
    def get_knowledge_context(self):
        """
        Get comprehensive knowledge context for LLM
        This will be sent with each query to improve accuracy
        """
        return {
            "truck_classifications": self.truck_classifications,
            "location_mappings": self.location_mappings,
            "terminology": self.terminology_dictionary,
            "conversation_patterns": self.conversation_patterns,
            "rate_intelligence": self.rate_intelligence,
            "instructions": {
                "normalization": "Use this knowledge to normalize truck types, locations, and terminology",
                "classification": "Map all variations to standard categories",
                "context_understanding": "Understand regional language mixing and industry slang",
                "rate_validation": "Use rate intelligence for market reasonableness checks"
            }
        }
    
    def get_truck_type_aliases(self, truck_type):
        """Get all aliases for a specific truck type"""
        if truck_type in self.truck_classifications:
            return self.truck_classifications[truck_type].get("aliases", [])
        return []
    
    def normalize_location(self, location_text):
        """Find standard location name from variations"""
        location_lower = location_text.lower()
        
        for city, data in self.location_mappings["major_cities"].items():
            if location_lower == city or location_lower in [alias.lower() for alias in data["aliases"]]:
                return data["primary"]
        
        return location_text  # Return original if not found
    
    def get_rate_estimate(self, truck_type, route_distance_km, seasonal_factor=1.0):
        """Get estimated rate based on truck type and distance"""
        base_rates = self.rate_intelligence["base_rates_per_km"]
        
        # Find matching truck type
        for rate_key, rates in base_rates.items():
            if truck_type.lower() in rate_key:
                base_rate = rates["avg"]
                total_estimate = base_rate * route_distance_km * seasonal_factor
                return {
                    "estimated_rate": total_estimate,
                    "rate_range": {
                        "min": rates["min"] * route_distance_km * seasonal_factor,
                        "max": rates["max"] * route_distance_km * seasonal_factor
                    },
                    "per_km_rate": base_rate * seasonal_factor
                }
        
        return None

# Global instance
trucking_knowledge = TruckingKnowledgeBase()