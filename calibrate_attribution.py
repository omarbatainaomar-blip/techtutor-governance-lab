"""معايرة التحقق بالمعنى: بيطبع تشابه كل جملة مع أقرب مقطع، لأجوبة من المصادر وأجوبة من الذاكرة.
python calibrate_attribution.py > logs\\calib.txt 2>&1      (بدها Ollama شغّال، حوالي دقيقتين، ما بيستدعي نموذج المحادثة)
"""
import rag

CASES = [  # (نوع، السؤال للبحث، الفلتر، الجواب)
    ("SOURCE", "What is subnetting?", "networking",
     "Subnetting is the division of an IP network into several smaller subnetworks. This is done by using a subnet mask to "
     "determine which part of the IP address represents the network and which part represents the device. For example, if the "
     "IP address is 192.168.10.77/26, the number 26 means that the first 26 bits represent the network, and the remaining 6 bits "
     "represent the devices. The block size is 64, so subnets start at 0, 64, 128, and 192. Address 77 falls within the block "
     "that starts at 64, so the network address is 192.168.10.64, and the broadcast address is 192.168.10.127."),
    ("MEMORY", "What is subnetting?", "networking",
     "Subnetting is the process of dividing a large network into smaller subnets. This allows for better management and "
     "organization of the network. A network with an IP address range of 192.168.1.0 to 192.168.1.255 can be subnetted to create "
     "smaller subnets. This process helps in reducing the size of broadcast domains and improving network performance and security."),
    ("MEMORY", "How does BGP work?", None,
     "BGP routers exchange routing information by sending update messages. These messages contain a list of ASes that a packet "
     "must traverse to reach the destination. BGP uses attributes such as the AS path length, the local preference, and the "
     "multi-exit discriminator (MED) to select the best path. A BGP router will choose the route with the shortest AS path or "
     "the highest local preference, depending on the configuration."),
    ("SOURCE", "اشرحلي الـ recursion", None,
     "الاستدعاء الذاتي (recursion) هو تقنية تستدعي فيها الدالة نفسها على نسخة أصغر من المشكلة. تخيل أنك في طابور وتسأل الشخص "
     "الذي أمامك عن ترتيبه، فيسأل من أمامه حتى يصل السؤال لأول شخص فيجيب 1. الحالة الأساسية (base case) توقف الاستدعاء، وبدونها "
     "يحدث خطأ RecursionError. يمكن استخدام memoization عبر lru_cache لتجنب إعادة حساب نفس القيم."),
    ("SOURCE", "شو يعني overfitting؟ وضّح أكثر", None,
     "بشكل أبسط، النموذج يشبه طالباً يحفظ أجوبة امتحانات السنوات السابقة بدل أن يفهم المادة. في الامتحان القديم يحصل على علامة "
     "كاملة، لكن عندما تتغير الأسئلة يفشل. لهذا نراقب الفرق بين أداء النموذج على بيانات التدريب وأدائه على بيانات التحقق، وإذا اتسع "
     "الفرق فهذا علامة على فرط التخصيص."),
    ("MEMORY", "What is Docker?", None,
     "منصة الحاويات تعتمد على صور طبقية يتم بناؤها من ملف تعليمات. تشغَّل كل حاوية بعزل عن نظام التشغيل المضيف باستخدام مساحات "
     "الأسماء ومجموعات التحكم. يمكن نشر الحاويات على عدة خوادم باستخدام أدوات التنسيق التي توزع الحمل وتعيد تشغيل الحاويات المتعطلة."),
    ("MEMORY", "شو الفرق بين TCP و UDP؟", None,
     "بروتوكول QUIC طورته Google ويعمل فوق UDP ليجمع بين السرعة والموثوقية. يستخدم HTTP/3 هذا البروتوكول لتقليل زمن إنشاء الاتصال "
     "إلى رحلة واحدة. كما يدعم QUIC ترحيل الاتصال عند تغيير الشبكة من Wi-Fi إلى بيانات الجوال."),
]

for kind, q, topic, ans in CASES:
    hits = rag.retrieve_merged(q, [], topic)
    ratio, res = rag.attribute(ans, hits)
    print(f"\n### {kind} | {q} | hits={len(hits)} | supported ratio={ratio:.2f} (SIM>={rag.SUPPORT_SIM})")
    for s, label, sim in res:
        print(f"   {sim:.3f} {'['+label+']' if label else '   '}  {s[:90]}")
