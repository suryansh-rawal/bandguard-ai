// Grammar and spelling checks for the quick local review.
//
// Every rule here is a high-precision pattern with a safe automatic fix, so a
// flag is almost always a real error. Things that need real understanding of
// the sentence (run-ons, fragments, tense changes, word choice) are NOT covered
// here; they belong to the AI step on the backend.

/* ---------- helpers ---------- */

const norm = (v) => v.replace(/’/g, "'").toLowerCase();

// Keep the capitalisation of the original word.
function cased(orig, rep) {
  if (!rep) return rep;
  if (orig.length > 1 && orig === orig.toUpperCase() && /[A-Z]/.test(orig)) return rep.toUpperCase();
  if (/^[A-Z]/.test(orig)) return rep.charAt(0).toUpperCase() + rep.slice(1);
  return rep;
}

const whole = (m) => [m.index, m.index + m[0].length];
const prevWordOf = (text, index) =>
  ((text.slice(0, index).match(/([A-Za-z']+)\s+$/) || [])[1] || "").toLowerCase();
const AUX = /^(does|did|do|will|would|can|could|should|may|might|must|shall|to|let|lets|make|makes|made|had|have|has|not)$/;
const SENTENCE_START = /(^|[.!?]["')\]]*\s+|\n\s*)$/;

// A word must not continue into a compound like "all-in-one" or "a/b".
const END = "(?![\\w/-])";

const RULES = [];
const rule = (id, label, reason, re, fix) => RULES.push({ id, label, reason, re, fix });

/* ---------- spacing and punctuation ---------- */

rule("space", "Extra space", "Use a single space between words.", /(\S+) {2,}(\S+)/g, (m) => [
  ...whole(m),
  `${m[1]} ${m[2]}`,
]);

rule(
  "space-punct",
  "Space before punctuation",
  "Remove the space before the punctuation mark.",
  /([\w"')\]]) +([,;:.!?])(?![.\w])/g,
  (m) => (/\d/.test(m[1]) && m[2] === ":" ? null : [...whole(m), m[1] + m[2]])
);

rule(
  "space-after-comma",
  "Missing space",
  "Add a space after the comma or semicolon.",
  /([A-Za-z])([,;])(?=[A-Za-z])/g,
  (m) => [...whole(m), `${m[1]}${m[2]} `]
);

rule(
  "space-after-stop",
  "Missing space",
  "Add a space after the end of a sentence.",
  /(?<![\w./@:#-])([a-z]{2,})([.!?])(?=[A-Z][a-z])/g,
  (m) => [...whole(m), `${m[1]}${m[2]} `]
);

rule("punct-dup", "Repeated punctuation", "Use a single punctuation mark.", /([,;:])\1+|(?<!\.)\.\.(?!\.)/g, (m) => [
  ...whole(m),
  m[0][0],
]);

/* ---------- repeated words ---------- */

const SKIP_DUP = new Set(["that", "had", "very", "so", "no", "bye", "ha", "hey", "yes", "well", "knock"]);
rule("dup", "Repeated word", "This word appears twice in a row.", /\b([A-Za-z]+)(\s+)\1\b/gi, (m) =>
  SKIP_DUP.has(m[1].toLowerCase()) || m[2].includes("\n") ? null : [...whole(m), m[1]]
);

/* ---------- capital letters ---------- */

const ABBREVIATION = /^(e\.g|i\.e|etc|vs|approx|mr|mrs|ms|dr|st|inc|ltd|co|fig|vol|pp?|no|u\.s|a\.m|p\.m)$/;
rule(
  "cap",
  "Capital letter",
  "Start a sentence with a capital letter.",
  /(^\s*|[.!?]["')\]]*\s+|\n\s*)([a-z][A-Za-z'’-]*)/g,
  (m, text) => {
    const lead = m[1];
    const word = m[2];
    const start = m.index + lead.length;
    if (lead.trim().startsWith(".")) {
      if (text[m.index - 1] === ".") return null; // ellipsis
      const before = text.slice(0, m.index);
      const tok = ((before.match(/(\S+)$/) || [""])[0] + "").toLowerCase().replace(/^[("']+/, "");
      if (ABBREVIATION.test(tok)) return null;
    }
    if (/^[a-z]+[A-Z]/.test(word)) return null; // iPhone, eBay
    if (["www", "http", "https"].includes(word)) return null;
    const after = text.slice(start + word.length, start + word.length + 2);
    if (/^\.[a-z]/i.test(after) || after[0] === "@" || after[0] === "/") return null; // web address
    return [start, start + word.length, word.charAt(0).toUpperCase() + word.slice(1)];
  }
);

rule(
  "i",
  "Capital I",
  "The word “I” is always a capital letter.",
  /(?<![\w'’./@#(-])i(?=['’](?:m|ll|ve|d)\b|[\s,.!?;:]|$)(?!\.e\b)/g,
  (m) => [m.index, m.index + 1, "I"]
);

rule(
  "day-month",
  "Capital letter",
  "Days and months start with a capital letter.",
  /\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|april|june|july|august|september|october|november|december)\b/g,
  (m) => [...whole(m), m[1].charAt(0).toUpperCase() + m[1].slice(1)]
);

/* ---------- apostrophes ---------- */

const CONTRACTION = {
  dont: "don't", doesnt: "doesn't", didnt: "didn't", cant: "can't", isnt: "isn't", arent: "aren't",
  wasnt: "wasn't", werent: "weren't", couldnt: "couldn't", wouldnt: "wouldn't", shouldnt: "shouldn't",
  havent: "haven't", hasnt: "hasn't", hadnt: "hadn't", youre: "you're", theyre: "they're",
  weve: "we've", ive: "I've", youve: "you've", theyve: "they've", thats: "that's", whats: "what's",
  heres: "here's", theres: "there's", wheres: "where's",
};
rule(
  "contraction",
  "Apostrophe",
  "This contraction needs an apostrophe.",
  new RegExp(`\\b(${Object.keys(CONTRACTION).join("|")})\\b`, "gi"),
  (m) => [...whole(m), cased(m[1], CONTRACTION[m[1].toLowerCase()])]
);

rule(
  "wont",
  "Apostrophe",
  "This contraction needs an apostrophe.",
  /\b(wont)(?=\s+(?:be|work|have|happen|do|go|need|let|stop|take|get|make|ever|give|help|allow|miss|disappoint|cost)\b)/gi,
  (m) => [...whole(m), cased(m[1], "won't")]
);

rule(
  "im",
  "Apostrophe",
  "Write “I’m” with a capital I and an apostrophe.",
  /\b([Ii]m)(?=\s+(?:going|not|a|an|the|so|very|happy|sure|here|just|also|really|still|now|glad|proud|excited|ready|looking|working|writing|using|trying|sorry)\b)/g,
  (m) => [...whole(m), "I'm"]
);

/* ---------- words that are easy to mix up ---------- */

rule(
  "its",
  "Its or it’s",
  "Use “it’s” when you mean “it is” or “it has”.",
  new RegExp(
    `\\b(its)(?=\\s+(?:a|an|not|been|going|very|so|too|just|really|also|now|still|always|never|only|easy|hard|important|possible|true|clear|okay|ok|time to)${END})`,
    "gi"
  ),
  (m) => [...whole(m), cased(m[1], "it's")]
);

rule(
  "its-own",
  "Its or it’s",
  "Use “its” (no apostrophe) to show that something belongs to it.",
  new RegExp(`\\b(it['’]s)(?=\\s+(?:own|features|customers|users|benefits)${END})`, "gi"),
  (m) => [...whole(m), cased(m[1], "its")]
);

rule(
  "your",
  "Your or you’re",
  "Use “you’re” when you mean “you are”.",
  new RegExp(
    `\\b(your)(?=\\s+(?:welcome|going|doing|a|an|not|the|all|so|very|always|never|just|really|also|now|still|only|already|ready|getting|using|making|taking|trying|looking)${END})`,
    "gi"
  ),
  (m) => [...whole(m), cased(m[1], "you're")]
);

rule(
  "youre-own",
  "Your or you’re",
  "Use “your” to show that something belongs to you.",
  new RegExp(`\\b(you['’]re)(?=\\s+(?:own|name|website|account|email|order|data)${END})`, "gi"),
  (m) => [...whole(m), cased(m[1], "your")]
);

rule(
  "their-there",
  "There or their",
  "Use “there” to say that something exists.",
  new RegExp(`\\b(their)(?=\\s+(?:is|are|was|were|has|have|been|isn['’]t|aren['’]t)${END})`, "gi"),
  (m) => [...whole(m), cased(m[1], "there")]
);

rule(
  "there-own",
  "There or their",
  "Use “their” to show that something belongs to them.",
  /\b(there)(?=\s+own\b)/gi,
  (m) => [...whole(m), cased(m[1], "their")]
);

rule(
  "theyre-own",
  "They’re or their",
  "Use “their” to show that something belongs to them.",
  new RegExp(`\\b(they['’]re)(?=\\s+(?:own|website|account|email|name)${END})`, "gi"),
  (m) => [...whole(m), cased(m[1], "their")]
);

rule(
  "their-theyre",
  "They’re or their",
  "Use “they’re” when you mean “they are”.",
  new RegExp(`\\b(their)(?=\\s+(?:going|not|a|an|the)${END})`, "gi"),
  (m) => [...whole(m), cased(m[1], "they're")]
);

rule(
  "then-than",
  "Then or than",
  "Use “than” to compare two things.",
  /\b(more|less|better|worse|faster|slower|bigger|smaller|higher|lower|greater|larger|longer|shorter|easier|cheaper|simpler|stronger|rather|older|newer|smarter|lighter|heavier|fewer)(\s+)then\b/gi,
  (m) => [...whole(m), `${m[1]}${m[2]}than`]
);

rule(
  "to-too",
  "To or too",
  "Use “too” when you mean “excessively”.",
  /\b(to)(\s+)(much|many|expensive|complicated)(?!\s+of\b)(?![\w-])/gi,
  (m) => [...whole(m), `${cased(m[1], "too")}${m[2]}${m[3]}`]
);

rule(
  "of-have",
  "Could have",
  "Write “have”, not “of”, after could, should, would, must or might.",
  /\b(could|should|would|must|might)(\s+)of\b/gi,
  (m) => [...whole(m), `${m[1]}${m[2]}have`]
);

rule(
  "affect-effect",
  "Affect or effect",
  "As a noun, the word is “effect”.",
  /\b(the|an?|no|any|this|that|its|their|our|your|positive|negative|big|major|huge|real|great)(\s+)affect(s?)(?=\s+(?:of|on)\b)/gi,
  (m) => [...whole(m), `${m[1]}${m[2]}effect${m[3]}`]
);

rule(
  "lose",
  "Lose or loose",
  "The verb is “lose”. “Loose” means not tight.",
  /\b(will|to|not|don['’]t|can['’]t|could|might|may|would|never|you|we|they)(\s+)loose\b/gi,
  (m) => [...whole(m), `${m[1]}${m[2]}lose`]
);

rule(
  "me-i",
  "Me or I",
  "After “between”, use “me”.",
  /\b(between\s+(?:you|him|her|them|us)\s+and\s+)I\b/g,
  (m) => [m.index + m[1].length, m.index + m[0].length, "me"]
);

/* ---------- subject and verb ---------- */

const PLURAL_VERB = { is: "are", was: "were", has: "have", does: "do", "doesn't": "don't" };
rule(
  "agree-plural",
  "Subject-verb agreement",
  "Use the plural verb with “they”, “we”, “you”, “these” and “those”.",
  /\b(they|we|you|these|those)(\s+)(is|was|has|does|doesn['’]t)\b/gi,
  (m) => [...whole(m), `${m[1]}${m[2]}${cased(m[3], PLURAL_VERB[norm(m[3])])}`]
);

const SINGULAR_VERB = {
  are: "is", were: "was", have: "has", "don't": "doesn't",
  "aren't": "isn't", "weren't": "wasn't", "haven't": "hasn't",
};
const HE_SHE_IT = new Set(["he", "she", "it", "this"]);
rule(
  "agree-singular",
  "Subject-verb agreement",
  "Use the singular verb with “he”, “she”, “it”, “this” and “everyone”.",
  /\b(he|she|it|this|everyone|everybody|someone|somebody|anyone|anybody|nobody|everything|something|nothing)(\s+)(are|were|have|don['’]t|aren['’]t|weren['’]t|haven['’]t)\b/gi,
  (m, text) => {
    const subj = m[1].toLowerCase();
    const verb = norm(m[3]);
    if (verb === "were" && HE_SHE_IT.has(subj)) return null; // "if it were"
    if (verb === "don't" && !HE_SHE_IT.has(subj)) return null; // "everyone don't" can be a command
    if ((verb === "have" || verb === "haven't") && AUX.test(prevWordOf(text, m.index))) return null; // "does it have"
    return [...whole(m), `${m[1]}${m[2]}${cased(m[3], SINGULAR_VERB[verb])}`];
  }
);

const I_VERB = { is: "am", are: "am", has: "have", does: "do", "doesn't": "don't" };
rule(
  "agree-i",
  "Subject-verb agreement",
  "Use “am” and “have” with “I”.",
  /\bI(\s+)(is|are|has|does|doesn['’]t)\b/g,
  (m) => [...whole(m), `I${m[1]}${I_VERB[norm(m[2])]}`]
);

rule(
  "there-plural",
  "Subject-verb agreement",
  "Use “there are” before a plural.",
  /\bthere(\s+)(is|was)(\s+)(many|several|multiple|numerous|few|a few|two|three|four|five|six|seven|eight|nine)(?![\w-])/gi,
  (m) => [
    ...whole(m),
    `${m[0].slice(0, 5)}${m[1]}${m[2].toLowerCase() === "is" ? "are" : "were"}${m[3]}${m[4]}`,
  ]
);

rule(
  "there-an",
  "Subject-verb agreement",
  "Use “there is” before “an”.",
  /\bthere(\s+)are(\s+)an\b/gi,
  (m) => [...whole(m), `${m[0].slice(0, 5)}${m[1]}is${m[2]}an`]
);

rule(
  "this-plural",
  "This or these",
  "Use “these” before a plural noun.",
  /\b(this)(\s+)(apps|products|features|customers|teams|tools|services|items|ways|years|days|things|users|clients|people|employees)\b/gi,
  (m) => [...whole(m), `${cased(m[1], "these")}${m[2]}${m[3]}`]
);

const PAST_TO_BASE = {
  went: "go", came: "come", saw: "see", did: "do", ate: "eat", took: "take", made: "make", gave: "give",
  knew: "know", wrote: "write", bought: "buy", said: "say", thought: "think", found: "find", told: "tell",
  left: "leave", felt: "feel", got: "get", had: "have", ran: "run", began: "begin", spoke: "speak",
  sent: "send", paid: "pay",
};
rule(
  "did-base",
  "Verb form",
  "After “didn’t”, use the base form of the verb.",
  new RegExp(`\\b(did(?:n['’]t| not))(\\s+)(${Object.keys(PAST_TO_BASE).join("|")})\\b`, "gi"),
  (m) => [...whole(m), `${m[1]}${m[2]}${PAST_TO_BASE[m[3].toLowerCase()]}`]
);

/* ---------- much, many and uncountable nouns ---------- */

rule(
  "many-much",
  "Much or many",
  "Use “much” with things you cannot count.",
  /\bmany(\s+)(money|advice|stuff|water)\b/gi,
  (m) => [...whole(m), `${cased(m[0].slice(0, 4), "much")}${m[1]}${m[2]}`]
);

rule(
  "much-many",
  "Much or many",
  "Use “many” with things you can count.",
  /\bmuch(\s+)(people|customers|products|users|teams|apps|features|reports|items|things|ways|options|plans|clients|employees|friends|days|years|reasons|problems|questions)\b/gi,
  (m) => [...whole(m), `${cased(m[0].slice(0, 4), "many")}${m[1]}${m[2]}`]
);

/* ---------- articles ---------- */

rule(
  "article",
  "A or an",
  "Use “an” before a vowel sound and “a” before a consonant sound.",
  /\b(an?|An?)(\s+)([A-Za-z][A-Za-z'’-]*)/g,
  (m, text) => {
    const [art, gap, word] = [m[1], m[2], m[3]];
    if (gap.includes("\n") || word.length < 2) return null;
    const lowerArt = art === art.toLowerCase();
    if (!lowerArt && !SENTENCE_START.test(text.slice(0, m.index))) return null; // "Plan A is"
    if (/^[A-Z]{2,}/.test(word) || /\d/.test(word)) return null; // acronyms and numbers
    const w = word.toLowerCase();
    if (/^[a-z]-/.test(w)) return null; // "an x-ray"
    const silentH = /^(hour|honest|honou?r|heir)/.test(w);
    const consonantSound = /^(uni|use|usu|uti|ubiq|ura|euro|eu[a-z]|one(?![a-z])|one-|once)/.test(w);
    const needsAn = (/^[aeiou]/.test(w) && !consonantSound) || silentH;
    if (art.toLowerCase() === "an" && /^h/.test(w) && !silentH) return null; // "an historic" is accepted
    const want = needsAn ? "an" : "a";
    if (art.toLowerCase() === want) return null;
    const newArt = lowerArt ? want : want.charAt(0).toUpperCase() + want.slice(1);
    return [...whole(m), `${newArt}${gap}${word}`];
  }
);

/* ---------- spelling ---------- */

const SPELLING = {
  recieve: "receive", recieved: "received", definately: "definitely", definitly: "definitely",
  seperate: "separate", occured: "occurred", occurence: "occurrence", untill: "until", wich: "which",
  beleive: "believe", begining: "beginning", goverment: "government", enviroment: "environment",
  accomodate: "accommodate", acheive: "achieve", adress: "address", arguement: "argument",
  calender: "calendar", comming: "coming", completly: "completely", concious: "conscious",
  dissapoint: "disappoint", embarass: "embarrass", existance: "existence", foward: "forward",
  freind: "friend", grammer: "grammar", happend: "happened", immediatly: "immediately",
  independant: "independent", knowlege: "knowledge", maintainance: "maintenance", neccessary: "necessary",
  necesary: "necessary", noticable: "noticeable", occassion: "occasion", persistant: "persistent",
  posession: "possession", prefered: "preferred", publically: "publicly", recomend: "recommend",
  recomendation: "recommendation", refered: "referred", relevent: "relevant", resturant: "restaurant",
  succesful: "successful", sucess: "success", tommorow: "tomorrow", truely: "truly", wierd: "weird",
  writting: "writing", teh: "the", adn: "and", taht: "that", waht: "what", thier: "their",
  becuase: "because", becasue: "because", exellent: "excellent", usefull: "useful", wonderfull: "wonderful",
  beautifull: "beautiful", carefull: "careful", sucessful: "successful", buisness: "business",
  bussiness: "business", custmer: "customer", costumer: "customer", compeny: "company", comapny: "company",
  servise: "service", feture: "feature", featuer: "feature", discout: "discount", dicsount: "discount",
  adveritsement: "advertisement", advertisment: "advertisement", managment: "management",
  developement: "development", intresting: "interesting", experiance: "experience", experiment: "experiment",
  irregardless: "regardless", alot: "a lot", noone: "no one", infact: "in fact", eachother: "each other",
  atleast: "at least", aswell: "as well", everytime: "every time", thankyou: "thank you",
  ofcourse: "of course", inbetween: "in between", loosing: "losing",
  informations: "information", advices: "advice", feedbacks: "feedback", softwares: "software",
  equipments: "equipment", furnitures: "furniture", knowledges: "knowledge", homeworks: "homework",
};
delete SPELLING.experiment; // a real word, kept out on purpose
rule(
  "spelling",
  "Spelling",
  "This word is misspelled.",
  new RegExp(`\\b(${Object.keys(SPELLING).join("|")})\\b`, "gi"),
  (m) => [...whole(m), cased(m[1], SPELLING[m[1].toLowerCase()])]
);

/* ---------- runner ---------- */

export function grammarIssues(text) {
  const out = [];
  for (const r of RULES) {
    for (const m of text.matchAll(r.re)) {
      const hit = r.fix(m, text);
      if (!hit) continue;
      const [start, end, rep] = hit;
      if (text.slice(start, end) === rep) continue;
      out.push({
        key: `g-${r.id}-${start}`,
        label: r.label,
        source: "Grammar",
        severity: "low",
        found: text.slice(start, end),
        start,
        end,
        reason: r.reason,
        suggestion: rep === "" ? "Remove it." : `Use “${rep}” instead.`,
        replacement: rep,
        fix: (t) => t.slice(0, start) + rep + t.slice(end),
      });
    }
  }
  return out;
}