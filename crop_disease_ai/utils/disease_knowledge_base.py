class DiseaseKnowledgeBase:
    def __init__(self):
        self.database = self._build_database()

    def _build_database(self):
        return {
            "Tomato Bacterial Spot": {
                "description": "Bacterial spot is a serious disease of tomatoes caused by Xanthomonas campestris pv. vesicatoria. It affects leaves, stems, and fruits, causing significant yield losses in warm, humid conditions.",
                "symptoms": [
                    "Small, water-soaked spots on leaves that turn brown to black",
                    "Spots may have yellow halos surrounding them",
                    "Lesions on stems and petioles",
                    "Raised, scabby spots on green and ripe fruits",
                    "Leaf yellowing and defoliation in severe cases"
                ],
                "causes": [
                    "Bacterial pathogen Xanthomonas campestris pv. vesicatoria",
                    "Spread through splashing water, rain, and irrigation",
                    "Enters through natural openings or wounds",
                    "Survives in infected plant debris and on seeds",
                    "Favored by warm temperatures (25-30°C) and high humidity"
                ],
                "prevention": [
                    "Use disease-free seeds and certified transplants",
                    "Practice crop rotation with non-host crops for 3-4 years",
                    "Avoid overhead irrigation; use drip irrigation instead",
                    "Apply copper-based bactericides preventively",
                    "Remove and destroy infected plant debris",
                    "Use resistant tomato varieties when available"
                ],
                "treatment": [
                    "Apply copper-based bactericides (copper hydroxide, copper oxychloride)",
                    "Use streptomycin sulfate in severe cases",
                    "Apply fixed copper products every 7-10 days",
                    "Combine with mancozeb for improved efficacy",
                    "Remove severely infected plants to reduce spread"
                ],
                "organic_treatment": [
                    "Apply copper sulfate solution (3g/L water)",
                    "Use neem oil spray (5ml/L water) weekly",
                    "Apply Bacillus subtilis-based biofungicide",
                    "Use garlic-pepper spray as a preventive measure",
                    "Apply compost tea as foliar spray"
                ],
                "affected_crops": ["Tomato", "Pepper", "Eggplant"],
                "severity_indicators": {
                    "Mild": "Few spots on lower leaves only",
                    "Moderate": "Spots on multiple leaves with yellow halos",
                    "Severe": "Extensive leaf spotting, defoliation, fruit lesions"
                },
                "favorable_conditions": "Warm (25-30°C), humid weather with frequent rain or overhead irrigation"
            },
            "Tomato Early Blight": {
                "description": "Early blight is a common fungal disease of tomatoes caused by Alternaria solani. It affects leaves, stems, and fruits, and is most prevalent in warm, humid conditions.",
                "symptoms": [
                    "Dark brown to black spots with concentric rings (target spot pattern)",
                    "Yellowing of leaves around spots",
                    "Lower leaves affected first, progressing upward",
                    "Stem lesions that may girdle the stem",
                    "Sunken, dark lesions on fruits near the stem end"
                ],
                "causes": [
                    "Fungal pathogen Alternaria solani",
                    "Survives in infected plant debris and soil",
                    "Spread by wind, water, and tools",
                    "Enters through wounds or direct penetration",
                    "Favored by warm temperatures and high humidity"
                ],
                "prevention": [
                    "Plant resistant or tolerant varieties",
                    "Practice 3-year crop rotation away from solanaceous crops",
                    "Use mulch to prevent soil splash onto plants",
                    "Provide adequate spacing for air circulation",
                    "Water at base of plants, avoid overhead irrigation",
                    "Remove and destroy infected plant debris after harvest"
                ],
                "treatment": [
                    "Apply fungicides containing chlorothalonil, mancozeb, or copper",
                    "Use azoxystrobin or pyraclostrobin for preventive control",
                    "Apply difenoconazole or boscalid at first sign of disease",
                    "Rotate fungicide groups to prevent resistance",
                    "Apply every 7-10 days during favorable conditions"
                ],
                "organic_treatment": [
                    "Apply copper fungicide (approved for organic use)",
                    "Use Bacillus subtilis-based biofungicide",
                    "Apply sulfur dust or wettable sulfur",
                    "Use horsetail or chamomile tea as foliar spray",
                    "Apply neem oil formulation weekly"
                ],
                "affected_crops": ["Tomato", "Potato", "Eggplant", "Pepper"],
                "severity_indicators": {
                    "Mild": "Few spots on lower leaves, no defoliation",
                    "Moderate": "Spots on 30-50% of leaves, some yellowing",
                    "Severe": "Extensive defoliation, stem lesions, fruit infection"
                },
                "favorable_conditions": "Warm temperatures (24-30°C) with frequent rainfall and high humidity"
            },
            "Tomato Late Blight": {
                "description": "Late blight is a devastating disease of tomatoes caused by Phytophthora infestans. It rapidly destroys foliage and fruits, and was responsible for the Irish Potato Famine.",
                "symptoms": [
                    "Water-soaked, pale green spots on leaves that turn brown to black",
                    "White fungal growth on leaf undersides in humid conditions",
                    "Rapid expansion of lesions causing leaf death",
                    "Dark, firm lesions on stems",
                    "Brown, firm, greasy-looking spots on fruits"
                ],
                "causes": [
                    "Oomycete pathogen Phytophthora infestans",
                    "Spread by airborne spores",
                    "Thrives in cool, wet conditions",
                    "Can infect at any growth stage",
                    "Spores can travel long distances in wind"
                ],
                "prevention": [
                    "Plant resistant varieties (with Ph resistance genes)",
                    "Avoid planting near potato fields",
                    "Ensure good air circulation through proper spacing",
                    "Use drip irrigation instead of overhead sprinklers",
                    "Monitor weather forecasts for favorable conditions",
                    "Apply preventive fungicides before disease appears"
                ],
                "treatment": [
                    "Apply fungicides containing chlorothalonil, mancozeb for protection",
                    "Use metalaxyl/mefenoxam for systemic control",
                    "Apply dimethomorph or cymoxanil for curative action",
                    "Use copper-based fungicides for organic production",
                    "Apply every 5-7 days during wet weather"
                ],
                "organic_treatment": [
                    "Apply copper fungicide products approved for organic use",
                    "Use Bacillus subtilis-based products",
                    "Apply potassium bicarbonate solution",
                    "Use compost tea as foliar spray",
                    "Remove and destroy infected plants immediately"
                ],
                "affected_crops": ["Tomato", "Potato", "Other Solanaceous crops"],
                "severity_indicators": {
                    "Mild": "Few leaf spots on lower canopy",
                    "Moderate": "Lesions on multiple leaves, some stem infection",
                    "Severe": "Widespread foliage destruction, fruit infection, plant death"
                },
                "favorable_conditions": "Cool (15-22°C), wet conditions with high humidity and rain"
            },
            "Tomato Healthy": {
                "description": "The tomato plant appears healthy with no signs of disease infection. Continue preventive care and monitoring.",
                "symptoms": [
                    "No visible disease symptoms",
                    "Healthy green leaves without spots or discoloration",
                    "Normal growth and development",
                    "Vigorous stem and root system"
                ],
                "causes": ["No disease present"],
                "prevention": [
                    "Continue regular monitoring for early disease detection",
                    "Maintain proper nutrition and irrigation",
                    "Practice preventive fungicide application during favorable conditions",
                    "Maintain good field sanitation"
                ],
                "treatment": ["No treatment required"],
                "organic_treatment": ["Continue organic preventive practices"],
                "affected_crops": [],
                "severity_indicators": {},
                "favorable_conditions": "N/A"
            },
            "Potato Early Blight": {
                "description": "Early blight of potato is caused by Alternaria solani. It primarily affects leaves but can also infect tubers, causing yield losses and reducing tuber quality.",
                "symptoms": [
                    "Dark brown to black spots with concentric rings on lower leaves",
                    "Leaf yellowing and necrosis around lesions",
                    "Lesions progress upward from older leaves",
                    "Dark, sunken lesions on tubers",
                    "Severe defoliation in advanced stages"
                ],
                "causes": [
                    "Fungal pathogen Alternaria solani",
                    "Survives in soil and infected plant debris",
                    "Spread by wind, water, and mechanical means",
                    "Infection favored by warm, humid conditions",
                    "Plants under stress more susceptible"
                ],
                "prevention": [
                    "Use certified disease-free seed potatoes",
                    "Practice 3-4 year crop rotation",
                    "Plant resistant varieties when available",
                    "Maintain optimal plant nutrition",
                    "Avoid overhead irrigation",
                    "Hilling to protect developing tubers"
                ],
                "treatment": [
                    "Apply chlorothalonil, mancozeb, or azoxystrobin",
                    "Use boscalid or difenoconazole for curative action",
                    "Begin applications when plants are 6-8 inches tall",
                    "Rotate fungicide chemistries",
                    "Apply every 7-10 days"
                ],
                "organic_treatment": [
                    "Apply copper-based fungicides",
                    "Use Bacillus subtilis products",
                    "Apply neem oil sprays",
                    "Use sulfur-based products"
                ],
                "affected_crops": ["Potato", "Tomato"],
                "severity_indicators": {
                    "Mild": "Few spots on lower leaves only",
                    "Moderate": "Spots on 30-50% of foliage",
                    "Severe": "Extensive defoliation, tuber infection"
                },
                "favorable_conditions": "Warm temperatures (24-30°C), high humidity, and plant stress"
            },
            "Potato Late Blight": {
                "description": "Late blight is the most destructive disease of potatoes worldwide, caused by Phytophthora infestans. It can destroy an entire field within days under favorable conditions.",
                "symptoms": [
                    "Water-soaked, pale green lesions on leaves",
                    "White fungal growth on leaf undersides",
                    "Rapid browning and death of foliage",
                    "Brown lesions on stems",
                    "Reddish-brown dry rot in tubers"
                ],
                "causes": [
                    "Oomycete Phytophthora infestans",
                    "Spread through airborne sporangia",
                    "Can survive in infected tubers",
                    "Favored by cool, wet weather",
                    "Extremely rapid disease progression"
                ],
                "prevention": [
                    "Use certified disease-free seed potatoes",
                    "Plant resistant varieties",
                    "Destroy cull piles and volunteer potatoes",
                    "Apply preventive fungicides before infection",
                    "Monitor weather conditions closely"
                ],
                "treatment": [
                    "Apply metalaxyl or mefenoxam for systemic control",
                    "Use mancozeb + metalaxyl combinations",
                    "Apply chlorothalonil, cymoxanil, or dimethomorph",
                    "Treatment every 5-7 days in wet weather",
                    "Remove and destroy infected plants"
                ],
                "organic_treatment": [
                    "Apply copper hydroxide or copper sulfate",
                    "Use Bacillus subtilis products",
                    "Immediately remove infected plants",
                    "Improve air circulation"
                ],
                "affected_crops": ["Potato", "Tomato"],
                "severity_indicators": {
                    "Mild": "Few leaf lesions, limited spread",
                    "Moderate": "Multiple lesions, some stem infection",
                    "Severe": "Rapid foliage destruction, tuber infection"
                },
                "favorable_conditions": "Cool (15-22°C), wet weather with free moisture on leaves"
            },
            "Rice Leaf Blast": {
                "description": "Rice blast is a devastating fungal disease caused by Magnaporthe oryzae. It affects all above-ground parts of the rice plant and is one of the most destructive rice diseases worldwide.",
                "symptoms": [
                    "Diamond-shaped lesions with gray centers and dark borders",
                    "Lesions on leaves, nodes, necks, and panicles",
                    "Neck blast causes panicle to break and fall over",
                    "Leaf lesions coalesce causing leaf death",
                    "Partial or complete blanking of grains"
                ],
                "causes": [
                    "Fungal pathogen Magnaporthe oryzae",
                    "Spread by airborne spores",
                    "High nitrogen fertilization increases susceptibility",
                    "Favored by high humidity and moderate temperatures",
                    "Survives in infected straw and seeds"
                ],
                "prevention": [
                    "Plant resistant varieties",
                    "Balanced nitrogen fertilization",
                    "Avoid dense planting",
                    "Maintain proper water management",
                    "Remove infected crop residues",
                    "Use certified disease-free seeds"
                ],
                "treatment": [
                    "Apply tricyclazole or isoprothiolane",
                    "Use azoxystrobin or trifloxystrobin",
                    "Apply edifenphos or kitazin",
                    "Treatment at booting and heading stages",
                    "Rotate fungicides to prevent resistance"
                ],
                "organic_treatment": [
                    "Apply neem cake and neem oil",
                    "Use silica-based products",
                    "Apply Trichoderma biofungicide",
                    "Use pseudomonas fluorescens sprays"
                ],
                "affected_crops": ["Rice"],
                "severity_indicators": {
                    "Mild": "Few lesions on lower leaves",
                    "Moderate": "Lesions on leaves and some nodes",
                    "Severe": "Neck blast, panicle infection, significant yield loss"
                },
                "favorable_conditions": "High humidity (>90%), moderate temperatures (24-28°C), prolonged leaf wetness"
            },
            "Wheat Brown Rust": {
                "description": "Brown rust (leaf rust) of wheat is caused by Puccinia triticina. It is the most common rust disease of wheat and can cause significant yield losses under favorable conditions.",
                "symptoms": [
                    "Small, circular to oval brown pustules on leaves",
                    "Pustules primarily on upper leaf surface",
                    "Pustules contain brown urediniospores",
                    "Leaves may turn yellow and die prematurely",
                    "Reduced grain filling and yield"
                ],
                "causes": [
                    "Fungal pathogen Puccinia triticina",
                    "Urediniospores spread by wind",
                    "Requires living host to survive",
                    "Favored by moderate temperatures and humidity",
                    "Can overwinter on volunteer wheat"
                ],
                "prevention": [
                    "Plant resistant varieties with Lr genes",
                    "Eliminate volunteer wheat",
                    "Avoid early planting",
                    "Balanced fertilization",
                    "Monitor and scout regularly"
                ],
                "treatment": [
                    "Apply triazole fungicides (tebuconazole, propiconazole)",
                    "Use strobilurin fungicides (azoxystrobin)",
                    "Apply at flag leaf emergence if rust detected",
                    "Treatment may be needed on lower leaves",
                    "Consider yield potential before treating"
                ],
                "organic_treatment": [
                    "Apply sulfur-based fungicides",
                    "Use neem oil sprays",
                    "Apply compost tea regularly",
                    "Increase potash fertilization for resistance"
                ],
                "affected_crops": ["Wheat", "Barley"],
                "severity_indicators": {
                    "Mild": "Few pustules on lower leaves only",
                    "Moderate": "Pustules on flag leaf, some yield impact",
                    "Severe": "Heavy infection on flag leaf, substantial yield loss"
                },
                "favorable_conditions": "Temperatures 15-25°C with high humidity and leaf wetness"
            },
            "Corn Common Rust": {
                "description": "Common rust of corn is caused by Puccinia sorghi. It appears as elongated brown pustules on leaves and can reduce photosynthesis and yield in susceptible hybrids.",
                "symptoms": [
                    "Elongated, cinnamon-brown pustules on both leaf surfaces",
                    "Pustules erupt through the epidermis",
                    "Circular to elongated lesions",
                    "Severe infection causes leaf death",
                    "Reduced ear size and grain fill"
                ],
                "causes": [
                    "Fungal pathogen Puccinia sorghi",
                    "Urediniospores spread by wind",
                    "Requires living green tissue to infect",
                    "Favored by cool, humid weather",
                    "Survives on volunteer corn and alternate hosts"
                ],
                "prevention": [
                    "Plant resistant hybrids",
                    "Early planting to avoid favorable conditions",
                    "Manage volunteer corn",
                    "Balanced fertility program",
                    "Scout fields regularly"
                ],
                "treatment": [
                    "Apply triazole fungicides at tasseling",
                    "Use strobilurin fungicides for protection",
                    "Apply when rust reaches 5% severity on ear leaf",
                    "Treatment at silking provides best yield protection",
                    "Consider yield potential and hybrid susceptibility"
                ],
                "organic_treatment": [
                    "Apply sulfur-based products",
                    "Use neem formulations",
                    "Increase potassium nutrition",
                    "Biofungicide applications"
                ],
                "affected_crops": ["Corn", "Sweet Corn"],
                "severity_indicators": {
                    "Mild": "Few pustules, primarily below ear leaf",
                    "Moderate": "Pustules up to ear leaf, some yield impact",
                    "Severe": "Heavy infection above ear leaf, significant yield loss"
                },
                "favorable_conditions": "Cool (16-23°C), humid conditions with frequent dew"
            },
            "Cotton Leaf Curl": {
                "description": "Cotton leaf curl disease is caused by a begomovirus complex transmitted by whiteflies. It is a serious constraint to cotton production in many regions.",
                "symptoms": [
                    "Upward or downward curling of leaves",
                    "Vein thickening and darkening",
                    "Enation (leaf-like outgrowths) on veins",
                    "Stunted plant growth",
                    "Reduced boll formation and yield"
                ],
                "causes": [
                    "Cotton leaf curl virus (CLCuV) complex",
                    "Transmitted by whitefly (Bemisia tabaci)",
                    "Cannot be transmitted mechanically or through seed",
                    "Favored by high whitefly populations",
                    "Affects both Gossypium hirsutum and G. arboreum"
                ],
                "prevention": [
                    "Plant resistant or tolerant varieties",
                    "Control whitefly populations",
                    "Use reflective mulches to repel whiteflies",
                    "Avoid planting near infected fields",
                    "Remove weed hosts of virus and whitefly",
                    "Use barrier crops like maize or sorghum"
                ],
                "treatment": [
                    "No direct cure for viral infection",
                    "Control whitefly vector with insecticides",
                    "Apply imidacloprid or thiamethoxam for whitefly control",
                    "Use mineral oils to suppress whitefly",
                    "Remove and destroy infected plants",
                    "Support plant nutrition for better tolerance"
                ],
                "organic_treatment": [
                    "Apply neem oil for whitefly management",
                    "Use insecticidal soaps",
                    "Release natural predators (lacewings, ladybugs)",
                    "Apply garlic-chili spray",
                    "Yellow sticky traps for whitefly monitoring"
                ],
                "affected_crops": ["Cotton", "Okra", "Other Malvaceous crops"],
                "severity_indicators": {
                    "Mild": "Few curled leaves, minimal stunting",
                    "Moderate": "Prominent curling on multiple leaves, some stunting",
                    "Severe": "Severe curling, stunting, significant yield loss"
                },
                "favorable_conditions": "High whitefly populations, warm temperatures, dry conditions"
            },
            "Grapes Black Rot": {
                "description": "Black rot is a fungal disease of grapes caused by Guignardia bidwellii. It affects leaves, shoots, and berries, causing significant yield losses in susceptible varieties.",
                "symptoms": [
                    "Small, circular brown spots on leaves with dark borders",
                    "Black fruiting bodies (pycnidia) in leaf spots",
                    "Brown to black lesions on shoots",
                    "Berries develop brown spots that turn black and shrivel",
                    "Infected berries become hard black mummies"
                ],
                "causes": [
                    "Fungal pathogen Guignardia bidwellii",
                    "Overwinters in mummified berries",
                    "Spores spread by rain splash",
                    "Infection requires free water on plant surfaces",
                    "Ascospores and conidia both cause infection"
                ],
                "prevention": [
                    "Remove mummified berries and infected canes",
                    "Proper pruning for air circulation",
                    "Avoid overhead irrigation",
                    "Good weed management",
                    "Plant less susceptible varieties"
                ],
                "treatment": [
                    "Apply mancozeb, captan, or ziram protectively",
                    "Use myclobutanil or tebuconazole for curative action",
                    "Apply strobilurins (azoxystrobin) preventively",
                    "Begin treatment at shoot growth (3-5 inch stage)",
                    "Continue on 7-10 day schedule through fruit set"
                ],
                "organic_treatment": [
                    "Apply copper fungicides",
                    "Use sulfur-based products",
                    "Apply potassium bicarbonate",
                    "Remove infected plant parts immediately"
                ],
                "affected_crops": ["Grapes"],
                "severity_indicators": {
                    "Mild": "Few leaf spots, no berry infection",
                    "Moderate": "Multiple leaf spots, early berry infection",
                    "Severe": "Widespread leaf and berry infection, significant fruit loss"
                },
                "favorable_conditions": "Warm (20-27°C), wet weather during bloom through fruit set"
            },
            "Apple Apple Scab": {
                "description": "Apple scab is a fungal disease caused by Venturia inaequalis. It affects leaves and fruits, reducing photosynthesis and fruit quality.",
                "symptoms": [
                    "Olive-green to black spots on leaves",
                    "Leaf distortion and curling",
                    "Dark, scabby lesions on fruit",
                    "Cracked fruit surface",
                    "Premature leaf drop"
                ],
                "causes": [
                    "Fungal pathogen Venturia inaequalis",
                    "Overwinters in infected fallen leaves",
                    "Ascospores released in spring during rain",
                    "Infection requires leaf wetness",
                    "Continuous infection cycle during growing season"
                ],
                "prevention": [
                    "Plant resistant varieties",
                    "Rake and destroy fallen leaves in autumn",
                    "Proper pruning for air circulation",
                    "Apply nitrogen at proper rates to avoid lush growth",
                    "Monitor ascospore release with degree-day models"
                ],
                "treatment": [
                    "Apply captan, mancozeb, or sulfur for protection",
                    "Use myclobutanil or difenoconazole for post-infection",
                    "Apply strobilurins (pyraclostrobin) preventively",
                    "Begin at green tip stage",
                    "Continue on 7-day schedule through summer"
                ],
                "organic_treatment": [
                    "Apply sulfur products",
                    "Use copper fungicides",
                    "Apply potassium bicarbonate",
                    "Use neem oil formulations",
                    "Apply compost tea regularly"
                ],
                "affected_crops": ["Apple", "Pear"],
                "severity_indicators": {
                    "Mild": "Few leaf spots, no fruit infection",
                    "Moderate": "Multiple leaf spots, few fruit scabs",
                    "Severe": "Extensive leaf and fruit infection, crop loss"
                },
                "favorable_conditions": "Cool (15-20°C), wet spring weather with extended leaf wetness"
            },
            "Banana Panama Disease": {
                "description": "Panama disease (Fusarium wilt) of banana is caused by Fusarium oxysporum f. sp. cubense. It is a soil-borne vascular wilt disease that can destroy entire plantations.",
                "symptoms": [
                    "Yellowing and wilting of older leaves",
                    "Leaves collapse at the petiole",
                    "Vascular discoloration in rhizome and pseudostem",
                    "Longitudinal splitting of pseudostem base",
                    "Plant death before fruit production"
                ],
                "causes": [
                    "Fungal pathogen Fusarium oxysporum f. sp. cubense",
                    "Soil-borne pathogen that survives for decades",
                    "Enters through roots and colonizes vascular tissue",
                    "Spread through infected planting material",
                    "Spread by soil movement, water, and equipment"
                ],
                "prevention": [
                    "Use disease-free tissue culture plantlets",
                    "Plant resistant varieties (e.g., Cavendish resistant to Race 1)",
                    "Quarantine infected fields",
                    "Avoid movement of soil from infected areas",
                    "Use clean irrigation water",
                    "Disinfect farm equipment"
                ],
                "treatment": [
                    "No effective chemical cure available",
                    "Remove and destroy infected plants",
                    "Solarization of infested soil",
                    "Soil amendments with organic matter",
                    "Fumigation in severe cases"
                ],
                "organic_treatment": [
                    "Apply Trichoderma harzianum to soil",
                    "Use Pseudomonas fluorescens as biocontrol",
                    "Apply compost and neem cake",
                    "Soil solarization",
                    "Use biofumigation with mustard"
                ],
                "affected_crops": ["Banana", "Plantain"],
                "severity_indicators": {
                    "Mild": "Few yellow leaves, minimal vascular discoloration",
                    "Moderate": "Multiple yellow leaves, clear vascular browning",
                    "Severe": "Plant collapse, complete vascular necrosis"
                },
                "favorable_conditions": "Acid soils, poor drainage, temperatures 25-30°C"
            },
            "Mango Anthracnose": {
                "description": "Anthracnose of mango is caused by Colletotrichum gloeosporioides. It affects leaves, flowers, and fruits, causing significant pre- and post-harvest losses.",
                "symptoms": [
                    "Small, dark brown to black spots on leaves",
                    "Leaf spots expand to form irregular lesions",
                    "Flower blight causing blackening and dropping of flowers",
                    "Black, sunken lesions on fruit",
                    "Fruit rot development during ripening"
                ],
                "causes": [
                    "Fungal pathogen Colletotrichum gloeosporioides",
                    "Survives in infected plant debris",
                    "Spores spread by rain splash and wind",
                    "Latent infections on immature fruit",
                    "Favored by warm, humid conditions"
                ],
                "prevention": [
                    "Prune infected branches and improve air circulation",
                    "Remove and destroy fallen leaves and fruit",
                    "Proper tree spacing",
                    "Avoid overhead irrigation",
                    "Harvest fruit at proper maturity"
                ],
                "treatment": [
                    "Apply copper fungicides (copper oxychloride)",
                    "Use mancozeb or chlorothalonil protectively",
                    "Apply strobilurins (azoxystrobin) at flowering",
                    "Treatment during flowering and fruit development",
                    "Pre-harvest treatment for post-harvest control"
                ],
                "organic_treatment": [
                    "Apply copper-based products",
                    "Use neem oil sprays",
                    "Apply Bacillus subtilis biofungicide",
                    "Use horsetail extract spray"
                ],
                "affected_crops": ["Mango", "Cashew", "Papaya"],
                "severity_indicators": {
                    "Mild": "Few leaf spots, limited flower infection",
                    "Moderate": "Multiple leaf spots, significant flower blight",
                    "Severe": "Extensive leaf infection, severe fruit rot"
                },
                "favorable_conditions": "Warm (25-30°C), wet weather with high humidity"
            },
            "Chili Leaf Curl": {
                "description": "Chili leaf curl is caused by begomoviruses transmitted by whiteflies. It causes severe stunting and yield loss in chili and other solanaceous crops.",
                "symptoms": [
                    "Leaf curling and puckering",
                    "Yellowing and vein thickening",
                    "Stunted plant growth",
                    "Reduced fruit set and distorted fruits",
                    "Overall plant decline"
                ],
                "causes": [
                    "Chili leaf curl virus complex",
                    "Transmitted by whitefly (Bemisia tabaci)",
                    "Infected plants serve as virus reservoir",
                    "Weed hosts maintain virus and vector",
                    "Favored by warm, dry conditions"
                ],
                "prevention": [
                    "Use resistant varieties",
                    "Control whitefly with netting and reflective mulch",
                    "Remove weed hosts",
                    "Use barrier crops (maize, sorghum)",
                    "Plant trap crops for whitefly"
                ],
                "treatment": [
                    "No direct cure for viral infection",
                    "Control vector with systemic insecticides",
                    "Apply imidacloprid or thiamethoxam",
                    "Use mineral oil sprays",
                    "Remove infected plants",
                    "Support plant nutrition"
                ],
                "organic_treatment": [
                    "Apply neem oil for whitefly control",
                    "Use insecticidal soaps",
                    "Release natural enemies",
                    "Yellow sticky traps",
                    "Apply garlic-chili spray"
                ],
                "affected_crops": ["Chili", "Tomato", "Tobacco"],
                "severity_indicators": {
                    "Mild": "Slight leaf curling, minimal stunting",
                    "Moderate": "Prominent curling, some stunting",
                    "Severe": "Severe stunting, no fruit production"
                },
                "favorable_conditions": "High whitefly populations, warm temperatures, dry conditions"
            }
        }

    def search(self, query):
        if not query:
            return list(self.database.keys())
        query = query.lower()
        results = []
        for disease_name, info in self.database.items():
            if (query in disease_name.lower() or
                any(query in s.lower() for s in info.get("symptoms", [])) or
                any(query in c.lower() for c in info.get("causes", [])) or
                query in info.get("description", "").lower()):
                results.append(disease_name)
        return results if results else list(self.database.keys())

    def filter_by_crop(self, crop_name):
        if not crop_name:
            return list(self.database.keys())
        crop_name = crop_name.lower()
        results = [
            name for name, info in self.database.items()
            if crop_name in name.lower() or
            any(crop_name in c.lower() for c in info.get("affected_crops", []))
        ]
        return results if results else list(self.database.keys())

    def get_disease_info(self, disease_name):
        return self.database.get(disease_name, self._get_default_info())

    def get_all_diseases(self):
        return list(self.database.keys())

    def _get_default_info(self):
        return {
            "description": "Comprehensive disease information is being compiled for this condition.",
            "symptoms": [
                "Visible symptoms on leaves, stems, or fruits",
                "Changes in plant color or growth pattern",
                "Lesions, spots, or discoloration"
            ],
            "causes": [
                "Pathogen infection (fungal, bacterial, or viral)",
                "Environmental stress factors",
                "Nutritional imbalances"
            ],
            "prevention": [
                "Use disease-free planting material",
                "Practice crop rotation",
                "Maintain proper plant spacing",
                "Ensure balanced nutrition",
                "Regular field monitoring"
            ],
            "treatment": [
                "Consult local agricultural extension service",
                "Apply appropriate fungicides or bactericides",
                "Remove and destroy infected plants"
            ],
            "organic_treatment": [
                "Apply neem-based products",
                "Use biofungicides",
                "Implement integrated pest management"
            ],
            "affected_crops": [],
            "severity_indicators": {},
            "favorable_conditions": "Variable depending on pathogen"
        }
