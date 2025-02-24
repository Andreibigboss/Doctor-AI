const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');

// Răspunsuri predefinite pentru diferite tipuri de întrebări
const responses = {
    salut: [
        "Bună ziua! Cu ce vă pot ajuta?",
        "Bună! Sunt aici să vă ofer informații medicale generale.",
        "Salut! Cum vă pot ajuta astăzi?"
    ],
    durere: [
        "Pentru orice tip de durere persistentă, vă recomand să consultați un medic. Până atunci, asigurați-vă că vă odihniți și evitați activitățile care agravează durerea.",
        "Durerea poate fi un semn al corpului că ceva nu este în regulă. Vă recomand să programați o consultație medicală pentru o evaluare completă."
    ],
    răceală: [
        "Pentru răceală, vă recomand: odihnă, hidratare abundentă, și menținerea unei temperaturi confortabile în cameră. Dacă simptomele persistă mai mult de 7 zile, consultați medicul.",
        "Răceala este o infecție virală comună. Odihnă, lichide calde și vitamina C pot ajuta. Pentru simptome severe, consultați medicul."
    ],
    default: [
        "Îmi pare rău, dar nu pot oferi un diagnostic. Vă recomand să consultați un medic pentru o evaluare completă.",
        "Pentru siguranța dumneavoastră, vă sugerez să discutați cu un medic specialist despre această problemă.",
        "Aceasta este o situație care necesită evaluare medicală. Vă rog să contactați medicul dumneavoastră."
    ],
    febră: [
        "Febra poate fi un semn al unei infecții. Dacă temperatura depășește 38.5°C sau persistă mai mult de 3 zile, consultați medicul. Până atunci: odihniți-vă, beți multe lichide și puteți lua paracetamol pentru a reduce temperatura.",
        "Pentru febră, este important să vă hidratați bine și să vă odihniți. Monitorizați temperatura și consultați medicul dacă situația se agravează."
    ],
    stomac: [
        "Problemele stomacale pot avea multe cauze. Încercați să mâncați alimente ușoare și să beți suficiente lichide. Dacă simptomele persistă peste 24 de ore, consultați medicul.",
        "Pentru disconfort stomacal, evitați alimentele grase și condimentate. Odihna și hidratarea sunt importante. Consultați medicul dacă aveți dureri severe."
    ],
    alergii: [
        "Pentru simptome alergice, evitați contactul cu alergenii cunoscuți. Consultați un alergolog pentru teste specifice și tratament personalizat.",
        "Alergiile pot fi gestionate prin evitarea trigger-ilor și medicație specifică prescrisă de medic. Pentru reacții severe, solicitați imediat ajutor medical."
    ],
    anxietate: [
        "Anxietatea este o problemă comună. Încercați tehnici de respirație și relaxare. Pentru ajutor specializat, consultați un psiholog sau psihoterapeut.",
        "Stresul și anxietatea pot afecta sănătatea. Practicați exerciții de relaxare și mențineți un program de somn regulat. Nu ezitați să cereți ajutor profesional."
    ]
};

function getResponse(message) {
    message = message.toLowerCase();
    
    if (message.includes('salut') || message.includes('buna') || message.includes('bună')) {
        return responses.salut[Math.floor(Math.random() * responses.salut.length)];
    }
    if (message.includes('durere') || message.includes('doare')) {
        return responses.durere[Math.floor(Math.random() * responses.durere.length)];
    }
    if (message.includes('răceală') || message.includes('raceala') || message.includes('gripă')) {
        return responses.răceală[Math.floor(Math.random() * responses.răceală.length)];
    }
    if (message.includes('febră') || message.includes('febra') || message.includes('temperatura')) {
        return responses.febră[Math.floor(Math.random() * responses.febră.length)];
    }
    if (message.includes('stomac') || message.includes('greață') || message.includes('vomă')) {
        return responses.stomac[Math.floor(Math.random() * responses.stomac.length)];
    }
    if (message.includes('alergie') || message.includes('alergic')) {
        return responses.alergii[Math.floor(Math.random() * responses.alergii.length)];
    }
    if (message.includes('anxietate') || message.includes('stress') || message.includes('stres')) {
        return responses.anxietate[Math.floor(Math.random() * responses.anxietate.length)];
    }
    return responses.default[Math.floor(Math.random() * responses.default.length)];
}

function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    const formattedContent = content.replace(/\n/g, '<br>');
    messageDiv.innerHTML = formattedContent;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    try {
        addMessage(message, true);
        userInput.value = '';

        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message bot-message typing';
        typingIndicator.textContent = 'DocAI scrie...';
        chatMessages.appendChild(typingIndicator);

        // Folosim IP-ul local pe care îl vezi în terminal
        const response = await fetch('http://192.168.100.26:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        chatMessages.removeChild(typingIndicator);
        addMessage(data.response);

    } catch (error) {
        console.error('Error:', error);
        chatMessages.removeChild(document.querySelector('.typing'));
        addMessage('Îmi pare rău, a apărut o eroare. Vă rugăm să încercați din nou.');
    }
}

sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Adăugăm un mesaj de întâmpinare
window.addEventListener('load', () => {
    addMessage(`Bună ziua! Sunt DocAI, asistentul medical virtual. 
    Vă pot oferi informații generale despre sănătate și sfaturi medicale de bază. 
    Vă rog să rețineți că sunt doar un asistent virtual și nu înlocuiesc consultația cu un medic specialist.
    Cu ce vă pot ajuta astăzi?`);
});

const style = document.createElement('style');
style.textContent = `
    .typing {
        background: #f8fafc !important;
        color: #718096 !important;
        font-style: italic;
    }
`;
document.head.appendChild(style); 