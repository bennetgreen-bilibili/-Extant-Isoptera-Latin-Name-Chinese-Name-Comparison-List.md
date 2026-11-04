# -*- coding: utf-8 -*-
"""目级分科/亚科检索表（Hellemans et al. 2024 补充材料 Note 2）与新白蚁属分种检索表。

2024 年的分子系统学研究把等翅目重分为 13 科，原书（黄复生等，2000）的 6 科检索表
已不适用，故目级两表按 Nature Communications 15: 6724 的补充材料 Note 2 重译。
新白蚁属 Neotermes 的种表因原书 OCR 黏连无法机器还原，据原书逐条手工录入。
"""

HELSHORT = 'Hellemans 等（2024）'
BOOKSHORT = '黄复生等（2000）'

ORDSRC = ('据 Hellemans、Rocha、Wang 等（2024）Nature Communications 15: 6724 补充材料 Note 2'
          '「Key to extant families and subfamilies of Isoptera」的有翅成虫与兵蚁两套检索表译出。')
SFSRC = ('据 Hellemans 等（2024）Nature Communications 15: 6724 补充材料 Note 3'
         '「Key to subfamilies of Termitidae」（修订自 Krishna 等 2013）译出。')
BOOKSRC = '据黄复生等（2000）《中国动物志·昆虫纲·第十七卷·等翅目》译出。'

FAMNOTE = ('本表据 Hellemans 等（2024）补充材料 Note 2 译出，终点覆盖本站采用的 13 科，'
           '与原书（黄复生等，2000）的 6 科方案不同。胄白蚁科（Stolotermitidae）的 Stolotermitinae、'
           'Porotermitinae 与沙白蚁科（Psammotermitidae）的 Psammotermitinae、Prorhinotermitinae '
           '在原表为亚科级终点，本站未单设相应亚科页，故链接到所属科页并保留亚科名；'
           '原表标为「部分」（partim）的终点在条目文字中注明。')

NEONOTE = ('原书（黄复生等，2000）把扁胸新白蚁写作 Neotermes brachyotum，'
           '本站按现行拼写 Neotermes brachynotum 收载。')

ORDER_OVR = ('等翅目科的检索表', [('有翅成虫', [
  (1, [('跗节 3 节、4 节，或分节不明显的 5 节；后翅无臀叶；单眼有或无；后头沟缺（至多以折角或刻线表示）；前足基节无腹脊', 'to:2'),
       ('跗节明显分为 5 节；后翅有臀叶；有单眼；后头沟存在；前足基节有腹脊', 'fam:mastotermitidae')]),
  (2, [('无单眼；左上颚具 3 枚缘齿（LMt）；尾须 1—8 节［皱翅类 Teletisoptera］', 'to:3'),
       ('有单眼，或单眼缺而左上颚仅 2 枚缘齿；尾须 2 节［真等翅类 Icoisoptera］', 'to:7')]),
  (3, [('具中垫；跗节 5 节，有时分节不明显', 'to:4'),
       ('无中垫；跗节 4 节或 5 节', 'to:5')]),
  (4, [('右上颚端齿（RAt）长度等于或短于第一缘齿（RMt1）', 'fam:hodotermopsidae'),
       ('右上颚端齿长于第一缘齿', 'fam:archotermopsidae')]),
  (5, [('触角少于 20 节；右上颚具附齿［胄白蚁科 Stolotermitidae］', 'to:6'),
       ('触角多于 20 节；跗节 4 节；右上颚无附齿', 'fam:hodotermitidae')]),
  (6, [('跗节 4 节；腿节增粗；尾须 4—5 节；胫节距式 3:3:2 或 2:2:2（Stolotermitinae）', 'fam:stolotermitidae'),
       ('跗节 5 节；腿节不增粗；尾须 5 节；胫节距式 3:3:3 或 3:3:4（Porotermitinae）', 'fam:stolotermitidae')]),
  (7, [('有囟；跗节 3 节或 4 节；无中垫；左上颚多变［新等翅类 Neoisoptera］', 'to:8'),
       ('无囟；跗节 4 节；左上颚具 2 枚缘齿', 'fam:kalotermitidae')]),
  (8, [('前翅鳞明显覆盖后翅鳞；翅面具网状纹；前胸背板扁平', 'to:9'),
       ('前翅鳞不覆盖后翅鳞；翅面无网状纹；前胸背板马鞍形', 'fam:termitidae')]),
  (9, [('跗节 4 节', 'to:10'),
       ('跗节 3 节', 'fam:stylotermitidae')]),
  (10, [('左上颚端齿（LAt）短，其后具 3 枚明显缘齿', 'to:11'),
        ('左上颚端齿长，其后仅 1 枚明显缘齿', 'fam:serritermitidae')]),
  (11, [('前翅 M 脉（若存在）与 Cu 脉在翅鳞之外分叉［沙白蚁科 Psammotermitidae］', 'to:12'),
        ('前翅各脉在翅鳞之内独立起始', 'to:13')]),
  (12, [('前后翅鳞大小约相等，不重叠；头部无自囟至口上沟的沟（Psammotermitinae）', 'fam:psammotermitidae'),
        ('前后翅鳞大小不等，重叠；头部有自囟至口上沟的沟（Prorhinotermitinae）', 'fam:psammotermitidae')]),
  (13, [('后唇基无鼻状突，无自囟至下唇端部的沟', 'to:14'),
        ('后唇基具鼻状突，有自囟至唇基的狭沟', 'fam:rhinotermitidae')]),
  (14, [('头扁平，近三角形，后缘波状；前胸背板前缘具中突；翅密被刚毛', 'fam:termitogetonidae'),
        ('头不扁平，卵形，后缘平直；前胸背板前缘无中突；翅疏被刚毛', 'fam:heterotermitidae')]),
 ]), ('兵蚁', [
  (1, [('跗节 5 节，有时隐蔽（第 II 跗分节退化，仅腹面可见）', 'to:2'),
       ('跗节 3 节或 4 节', 'to:4')]),
  (2, [('前胸背板较小，窄于头，扁平；尾须 4—8 节；触角 19—27 节', 'to:3'),
       ('前胸背板大，与头等宽，马鞍形；尾须 4 节；触角 20—26 节', 'fam:mastotermitidae')]),
  (3, [('各足胫节均具侧刺；头后缘呈二叶状或均匀弧出', 'fam:archotermopsidae'),
       ('仅后足胫节具侧刺，中足胫节偶有 1 刺，前足胫节从无侧刺；头后缘均匀弧出', 'fam:hodotermopsidae')]),
  (4, [('头无囟', 'to:5'),
       ('头有囟［新等翅类］', 'to:8')]),
  (5, [('尾须长，1—5 节；触角 13—33 节', 'to:6'),
       ('尾须短，2 节；触角 10—21 节', 'fam:kalotermitidae')]),
  (6, [('前胸背板扁平；头壳或多或少扁平；后足腿节增粗；尾须 4—5 节；触角 13—19 节［胄白蚁科］', 'to:7'),
       ('前胸背板微呈马鞍形（前叶稍隆起）；头不扁平；后足腿节不增粗；尾须 1—5 节；触角 22—33 节', 'fam:hodotermitidae')]),
  (7, [('上颚短粗；头稍扁平；胫节距式 (2/3):(2/3/4):3（Porotermitinae）', 'fam:stolotermitidae'),
       ('上颚较长而不粗壮；头明显扁平；胫节距式 3:3:2 或 2:2:2（Stolotermitinae）', 'fam:stolotermitidae')]),
  (8, [('前胸背板扁平', 'to:9'),
       ('前胸背板明显马鞍形', 'fam:termitidae')]),
  (9, [('上颚内缘无锯齿，仅基部有时具少数小齿', 'to:10'),
       ('上颚沿整个内缘具锯齿', 'fam:serritermitidae')]),
  (10, [('跗节 4 节', 'to:11'),
        ('跗节 3 节', 'fam:stylotermitidae')]),
  (11, [('头具小囟，远离唇基基部', 'to:12'),
        ('头具大而圆的囟，位于唇基基部［乳白蚁属 Coptotermes；异白蚁科部分］', 'fam:heterotermitidae')]),
  (12, [('有自囟至唇基基部的沟', 'to:13'),
        ('无沟', 'to:14')]),
  (13, [('下唇端部具刷状毛；上颚具明显的缘齿', 'fam:rhinotermitidae'),
        ('下唇端部无刷状毛；上颚无明显缘齿［沙白蚁科部分］（Prorhinotermitinae）', 'fam:psammotermitidae')]),
  (14, [('头两侧圆', 'to:15'),
        ('头两侧近于平行［异白蚁科部分］', 'fam:heterotermitidae')]),
  (15, [('头近三角形、扁平，后缘波状；上颚除基部少数锯齿外无明显缘齿；前胸背板具前中突', 'fam:termitogetonidae'),
        ('头近矩形，后缘平直；上颚具明显缘齿；前胸背板无前中突［沙白蚁科部分］（Psammotermitinae）', 'fam:psammotermitidae')]),
 ])])

NEOTERMES_OVR = ('新白蚁属', [('兵蚁', [
  (1, [('头长（至颚基）大于头宽的 1.5 倍', 'to:2'),
       ('头长（至颚基）小于头宽的 1.5 倍', 'to:12')]),
  (2, [('前胸背板前缘中央凹口宽而浅；后颏最狭处较宽，其宽的 2 倍小于最大宽', 'to:3'),
       ('前胸背板前缘中央凹口较深；后颏腰区较宽，其宽的 2 倍大于最宽处', 'to:10')]),
  (3, [('后颏最宽区两侧缘平行对称，近似方形', 'to:4'),
       ('后颏最宽区两侧缘前后不对称，前部宽，后部狭', 'to:7')]),
  (4, [('体型大，后颏最宽区两侧中部略内凹', 'to:5'),
       ('体型小，后颏最宽区两侧几乎平直，不内凹', 'to:6')]),
  (5, [('眼与触角的间距约 0.25 mm；后颏较宽，最狭宽／长与最大宽／长指数分别为 0.12—0.16 和 0.25—0.35；前胸背板与头宽几乎相等', 'sp:neotermes-dubiocalcaratus'),
       ('眼与触角的间距约 0.20 mm；后颏较细长，最狭宽／长与最大宽／长指数分别为 0.08 和 0.24；前胸背板宽于头宽', 'sp:neotermes-angustigulus')]),
  (6, [('体较大，头宽 2.06—2.18 mm，前胸背板宽 2.29—2.59 mm；上颚外侧缘后半部呈波状，右上颚第 1 缘齿后切缘凹入、后端微凸', 'sp:neotermes-undulatus'),
       ('体略小，头宽 1.88—2.02 mm，前胸背板宽 2.08—2.40 mm；上颚外侧仅基部膨大，右上颚第 1 缘齿后切缘平直', 'sp:neotermes-longiceps')]),
  (7, [('前胸背板前缘中央凹口较浅；后颏最宽区两侧前宽后狭，中部略凹，呈两叶状', 'to:8'),
       ('前胸背板前缘中央凹口较深；后颏最宽区两侧中部无凹入，较平直', 'to:9')]),
  (8, [('触角 15 节，第 3 节膨大，明显大于第 2 节；头背中部略隆起', 'sp:neotermes-binovatus'),
       ('触角 16 节，第 3 节不膨大，短于第 2 节；头背缘较平坦', 'sp:neotermes-sinensis')]),
  (9, [('后颏最狭宽、最大宽与长之比指数均为 0.15，表面明显拱起', 'sp:neotermes-tuberogulus'),
       ('后颏最狭宽和最大宽分别是长的 1/10 和不及 1/3，呈棍棒状', 'sp:neotermes-fujianensis')]),
  (10, [('体形大；后颏最宽区两侧向后略缩狭，长不及最狭宽的 6 倍', 'sp:neotermes-fovefrons'),
        ('体略小；后颏最宽区两侧向后明显缩狭，长大于最狭宽的 7 倍', 'to:11')]),
  (11, [('体大型；前胸背板前、后缘中央明显凹入；右上颚第 2 缘齿后切缘较平直', 'sp:neotermes-miracapitalis'),
        ('体较小；前胸背板前、后缘中央凹口较浅；右上颚第 2 缘齿后切缘呈圆弧形凹', 'sp:neotermes-yunnanensis')]),
  (12, [('后颏最宽区两侧中部具凹入，呈两叶状', 'to:13'),
        ('后颏最宽区两侧中部无凹入，非两叶状', 'to:15')]),
  (13, [('触角第 3 节长于第 2 节；上唇前缘中央内凹；后颏长为最狭处的 6—7 倍；体较大', 'sp:neotermes-koshunensis'),
        ('触角第 3 节等于第 2 节；上唇前缘中央凸出；后颏长为最狭处的 7 倍；体略小', 'to:14')]),
  (14, [('头略狭长；前胸背板前缘浅凹弧，后缘中央略凹；触角第 3 节短于第 2 节', 'sp:neotermes-dolichognathus'),
        ('头部略短宽；前胸背板前缘凹口宽而深，后缘中央不凹、近平直；触角第 3 节长于第 2 节', 'sp:neotermes-humilis')]),
  (15, [('体略大；右上颚第 1 缘齿后切缘突起呈齿状；后颏略细长，长为最狭宽的 7—8 倍；头两侧近平行', 'to:16'),
        ('体略小；右上颚第 1 缘齿后切缘呈凹面；后颏稍粗短，长为最狭宽的 5—6 倍；头两侧前狭后宽', 'to:17')]),
  (16, [('头型明显宽而短；后颏最宽区两侧前宽后狭；前胸背板前缘凹口狭小；触角 14 节', 'sp:neotermes-amplilabralis'),
        ('头型较狭长；后颏最宽区两侧前后平直；前胸背板前缘凹呈 V 形，凹口深；触角 12 节', 'sp:neotermes-brachynotum')]),
  (17, [('左上颚短，其长小于头宽；后颏最宽区两侧平行；触角 14—16 节', 'sp:neotermes-sphenocephalus'),
        ('左上颚较长，其长大于头宽；后颏最宽区两侧前宽后狭；前胸背板前缘中央凹口较宽而深，中央不具切刻；触角 12 节', 'sp:neotermes-taishanensis')]),
 ])])

# ---------------------------------------------------------------------------
# 木白蚁科（Kalotermitidae）世界分属检索表
# 据 Krishna et al. (2013) Treatise on the Isoptera of the World 第 75—78 页
# "Key to the Genera of the Family Kalotermitidae"（源自 Krishna, 1961）译出。
# 原表分有翅成虫与兵蚁两套；化石属以 fos: 前缀标记，不链接本站页面。
KALOSRC = ('据 Krishna、Grimaldi、Krishna、Engel（2013）《Treatise on the Isoptera of the World》'
           '（Bulletin of the American Museum of Natural History 377）第 75—78 页'
           '「Key to the Genera of the Family Kalotermitidae」（源自 Krishna, 1961）译出。')
KRISHNASHORT = 'Krishna 等（2013）'
KALONOTE = ('世界分属检索表，含化石属 †Proelectrotermes 与 †Electrotermes；本站只收现存类群，'
            '化石属仅列名不加链接。原表据 Krishna（1961），未含本站另收的头长白蚁属'
            '（Longicaputermes）与罗伊辛白蚁属（Roisinitermes）。')

KALO_WORLD = ('木白蚁科分属检索表（世界）', [
 ('有翅成虫', [
  (1, [('前翅 M 脉与 Cu 脉在翅鳞之外共同起始；爪间突缺', 'to:2'),
       ('前翅 M 脉与 Cu 脉在翅鳞之内起始；爪间突有或缺', 'to:3')]),
  (2, [('左上颚（有翅成虫或拟工蚁）第 3 缘齿前缘长度超过第 1+2 缘齿后缘长度的 1.5 倍', 'gen:epicalotermes'),
       ('第 3 缘齿前缘明显较长，但通常不超过第 1+2 缘齿后缘长度的 1.5 倍', 'gen:bifiditermes+gen:bicornitermes')]),
  (3, [('中胫具 3 枚端距，并另有刺', 'to:4'),
       ('中胫仅具 3 枚端距，无附加刺', 'to:6')]),
  (4, [('中胫具 2 枚外刺和 1 枚内刺；仅化石', 'fos:Proelectrotermes'),
       ('中胫具 1—2 枚外刺，无内刺', 'to:5')]),
  (5, [('中胫具 2 枚外刺；仅化石', 'fos:Electrotermes'),
       ('中胫具 1 枚外刺；现生', 'gen:postelectrotermes')]),
  (6, [('左上颚第 3 缘齿前缘等于第 1+2 缘齿后缘', 'to:7'),
       ('左上颚第 3 缘齿前缘明显较长', 'to:16')]),
  (7, [('前翅 M 脉未骨化、细弱，大致居中于 Rs 与 Cu 之间，直达翅端', 'to:8'),
       ('前翅 M 脉骨化', 'to:9')]),
  (8, [('翅深色，具瘤状小突起；爪间突有', 'gen:kalotermes'),
       ('翅透明，无瘤突；爪间突缺', 'gen:pterotermes')]),
  (9, [('前翅 M 脉骨化，但强度不及 Rs', 'to:10'),
       ('前翅 M 脉骨化强度与 Rs 相同', 'to:12')]),
  (10, [('头与前胸背板密被长而波状的毛', 'gen:comatermes'),
        ('头与前胸背板被短刚毛，无长毛', 'to:11')]),
  (11, [('左上颚第 1+2 缘齿后缘具明显端齿，后缘略长于第 3 缘齿前缘', 'gen:paraneotermes'),
        ('第 1+2 缘齿后缘无端齿，均匀圆滑；后缘等于第 3 缘齿前缘', 'gen:ceratokalotermes')]),
  (12, [('Rs 不分枝；M 脉紧靠 Rs 直达翅端', 'to:13'),
        ('Rs 具分枝', 'to:14')]),
  (13, [('左上颚第 1+2 缘齿后缘与第 3 缘齿前缘交界处有明显角状缺刻', 'gen:glyptotermes'),
        ('左上颚上述交界处无明显角状缺刻', 'gen:calcaritermes')]),
  (14, [('M 脉极短小，在近翅缝处与 Rs 汇合', 'gen:rugitermes'),
        ('M 脉紧靠并平行于 Rs 直达翅端', 'to:15')]),
  (15, [('前翅鳞前缘凸；复眼直径 0.46—0.78 mm', 'gen:neotermes'),
        ('前翅鳞前缘近直；复眼直径 0.43 mm', 'gen:eucryptotermes')]),
  (16, [('M 脉稍骨化，与 Rs 的距离较与 Cu 近', 'gen:proneotermes'),
        ('M 脉未骨化，大致居中于 Rs 与 Cu 之间', 'to:17')]),
  (17, [('M 脉在翅中部或中部之后向上弯，与 Rs 汇合', 'gen:procryptotermes+gen:cryptotermes'),
        ('M 脉直达翅端', 'to:18')]),
  (18, [('爪间突始终缺', 'gen:marginitermes+gen:allotermes'),
        ('爪间突通常有，偶缺', 'gen:incisitermes+gen:tauritermes')]),
 ]),
 ('兵蚁', [
  (1, [('中胫具 1 枚外刺', 'gen:postelectrotermes'),
       ('中胫无刺', 'to:2')]),
  (2, [('前胫外侧近端部具 1 枚粗大显著的距，远大于 2 枚端距', 'gen:calcaritermes'),
       ('前胫端距不增大', 'to:3')]),
  (3, [('头短，强堵口型（头前部平截，可用头堵住巢口）', 'to:4'),
       ('头长或短，非堵口型，前部以约 20°—45° 倾斜；具或不具前侧突', 'to:8')]),
  (4, [('前胸背板前缘锯齿状', 'to:5'),
       ('前胸背板前缘平整，不呈锯齿状', 'to:7')]),
  (5, [('前胸背板前缘呈锐锯齿状；头二叶状，叶间区域凹陷；头顶与额之间无脊', 'gen:bicornitermes'),
       ('前胸背板前缘波状，具弱或细锯齿；头顶与额之间有脊', 'to:6')]),
  (6, [('头前部强烈凹入（勺状）；触角窝位于距头前部 1/3—1/2 头长处', 'gen:eucryptotermes'),
       ('头前部垂直，不强烈凹入；触角窝靠近上颚侧基', 'gen:cryptotermes')]),
  (7, [('头顶与额之间脊明显；头前部不垂直；触角第 3 节大，棒状', 'gen:procryptotermes'),
       ('头顶与额之间无脊；头前部垂直；触角第 3 节不大', 'gen:glyptotermes|部分种+gen:kalotermes|部分种')]),
  (8, [('前胸背板前缘无深凹或深缺刻', 'to:9'),
       ('前胸背板前缘深凹或具深缺刻', 'to:13')]),
  (9, [('头前部具显著脊，由触角背缘向中央延伸而成', 'gen:rugitermes'),
       ('头无显著脊', 'to:10')]),
  (10, [('头通常具明显前侧突，有时呈堵口型', 'gen:glyptotermes'),
        ('头长，无明显前侧突', 'to:11')]),
  (11, [('上颚相对头壳其余部分短', 'to:12'),
        ('上颚长，相对头壳不短', 'gen:kalotermes+gen:neotermes')]),
  (12, [('后颏前部很宽；拟工蚁上颚如图 38B', 'gen:paraneotermes'),
        ('后颏前部不很宽；头前部斜面凹入', 'gen:comatermes')]),
  (13, [('头两侧明显圆；后颏基部有骨化肿胀', 'gen:pterotermes'),
        ('头两侧几乎平直；后颏基部无肿胀', 'to:14')]),
  (14, [('触角第 3 节很大，长度等于其后 5—7 节之和；头顶与额之间有脊', 'gen:marginitermes'),
        ('触角第 3 节不及其后 5—7 节之和', 'to:15')]),
  (15, [('头背腹扁平', 'to:16'),
        ('头厚', 'to:17')]),
  (16, [('头自中部附近向前倾斜；上颚相对头壳长且强烈弯曲；腿节不肿胀', 'gen:epicalotermes'),
        ('头不自中部向前倾斜；上颚相对头壳短；腿节强烈肿胀', 'gen:incisitermes')]),
  (17, [('触角窝前下方具角状突', 'gen:allotermes'),
        ('无角状突', 'to:18')]),
  (18, [('头具明显前侧突', 'to:19'),
        ('头前侧突不明显', 'to:20')]),
  (19, [('触角第 3 节特化，较第 4 节长且色深；前胸背板前缘明显波状', 'gen:tauritermes'),
        ('触角第 3 节不特化，与第 4 节等长；前胸背板前缘微弱波状', 'gen:ceratokalotermes')]),
  (20, [('腿节肿胀；头前部深色；头顶与额之间有弱脊', 'gen:proneotermes'),
        ('腿节不肿胀；头顶与额之间无脊', 'gen:bifiditermes')]),
 ]),
])
